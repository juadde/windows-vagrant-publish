#!/usr/bin/env python3
"""Upload a Vagrant box to an S3-compatible bucket and update its Vagrant catalog.

Works with any S3-compatible object storage (Cloudflare R2, Oracle Cloud Object
Storage, Backblaze B2, AWS S3, ...). The catalog is a standard Vagrant "box
metadata" JSON file (https://developer.hashicorp.com/vagrant/docs/boxes/format#box-metadata)
stored next to the boxes, so `vagrant box add`, `vagrant box outdated` and
`vagrant box update` keep working like with a registry.

Bucket layout:
    <box>.json                      the catalog
    <box>/<version>/<provider>-<arch>.box

Environment variables:
    S3_ENDPOINT_URL        S3 API endpoint (e.g. https://<account>.r2.cloudflarestorage.com)
    S3_BUCKET              bucket name
    S3_PUBLIC_URL          public base URL of the bucket (e.g. https://boxes.example.com)
    AWS_ACCESS_KEY_ID      S3 access key
    AWS_SECRET_ACCESS_KEY  S3 secret key
    AWS_DEFAULT_REGION     optional (defaults to "auto", which is what R2 expects)
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def version_key(version: str):
    return tuple(int(p) if p.isdigit() else p for p in version.split("."))


def load_catalog(s3, bucket: str, key: str, box_name: str) -> dict:
    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        return json.loads(body)
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
            return {"name": box_name, "versions": []}
        raise


def delete_versions(s3, bucket: str, short_name: str, versions: list) -> None:
    for old in versions:
        prefix = f"{short_name}/{old['version']}/"
        print(f"Deleting old version {prefix}...", flush=True)
        listing = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        for obj in listing.get("Contents", []):
            s3.delete_object(Bucket=bucket, Key=obj["Key"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--box", required=True, type=Path, help="path to the .box file")
    parser.add_argument("--box-name", required=True, help="Vagrant box name, e.g. kppqju77/windows-11-fr-input")
    parser.add_argument("--version", required=True, help="box version, e.g. 20261101.46")
    parser.add_argument("--provider", default="libvirt")
    parser.add_argument("--architecture", default="amd64")
    parser.add_argument("--description", default="")
    parser.add_argument("--keep", type=int, default=1, help="number of versions to keep (older ones are deleted)")
    parser.add_argument(
        "--prune-first", action="store_true",
        help="delete versions that will be dropped before uploading (for tight storage quotas; "
             "the catalog briefly points to deleted files)",
    )
    args = parser.parse_args()

    bucket = os.environ["S3_BUCKET"]
    public_url = os.environ["S3_PUBLIC_URL"].rstrip("/")
    s3 = boto3.client(
        "s3",
        endpoint_url=os.environ["S3_ENDPOINT_URL"],
        region_name=os.environ.get("AWS_DEFAULT_REGION", "auto"),
    )

    short_name = args.box_name.split("/")[-1]
    catalog_key = f"{short_name}.json"
    box_key = f"{short_name}/{args.version}/{args.provider}-{args.architecture}.box"

    catalog = load_catalog(s3, bucket, catalog_key, args.box_name)
    catalog["name"] = args.box_name
    if args.description:
        catalog["description"] = args.description
    versions = {v["version"]: v for v in catalog.get("versions", [])}
    entry = versions.setdefault(args.version, {"version": args.version, "providers": []})
    ordered = sorted(versions.values(), key=lambda v: version_key(v["version"]), reverse=True)
    kept, removed = ordered[: args.keep], ordered[args.keep:]

    if args.prune_first:
        delete_versions(s3, bucket, short_name, removed)

    print(f"Computing sha256 of {args.box}...", flush=True)
    checksum = sha256sum(args.box)

    print(f"Uploading {args.box} to s3://{bucket}/{box_key}...", flush=True)
    s3.upload_file(
        str(args.box), bucket, box_key,
        ExtraArgs={"ContentType": "application/octet-stream"},
        Config=TransferConfig(multipart_chunksize=256 * 1024 * 1024, max_concurrency=8),
    )

    entry["providers"] = [
        p for p in entry["providers"]
        if not (p["name"] == args.provider and p.get("architecture") == args.architecture)
    ]
    entry["providers"].append({
        "name": args.provider,
        "url": f"{public_url}/{box_key}",
        "checksum_type": "sha256",
        "checksum": checksum,
        "architecture": args.architecture,
        "default_architecture": True,
    })
    catalog["versions"] = kept

    # Vagrant detects a catalog by its application/json Content-Type.
    s3.put_object(
        Bucket=bucket, Key=catalog_key,
        Body=(json.dumps(catalog, indent=2) + "\n").encode(),
        ContentType="application/json",
        CacheControl="no-cache",
    )

    if not args.prune_first:
        delete_versions(s3, bucket, short_name, removed)

    print(f"Catalog updated: {public_url}/{catalog_key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
