#!/usr/bin/env python3
"""Upload a Vagrant box to Hugging Face and update its Vagrant catalog (metadata) file.

The catalog is a standard Vagrant "box metadata" JSON file
(https://developer.hashicorp.com/vagrant/docs/boxes/format#box-metadata),
meant to be served by GitHub Pages so that `vagrant box add`, `vagrant box
outdated` and `vagrant box update` keep working like with a registry.

Requires the HF_TOKEN environment variable (a Hugging Face write token).
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from huggingface_hub import HfApi


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def version_key(version: str):
    return tuple(int(p) if p.isdigit() else p for p in version.split("."))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--box", required=True, type=Path, help="path to the .box file")
    parser.add_argument("--box-name", required=True, help="Vagrant box name, e.g. kppqju77/windows-11-fr-input")
    parser.add_argument("--version", required=True, help="box version, e.g. 20261101.46")
    parser.add_argument("--provider", default="libvirt")
    parser.add_argument("--architecture", default="amd64")
    parser.add_argument("--description", default="")
    parser.add_argument("--hf-repo", required=True, help="Hugging Face repository, e.g. user/windows-vagrant")
    parser.add_argument("--hf-repo-type", default="model", choices=["model", "dataset"])
    parser.add_argument("--catalog", required=True, type=Path, help="catalog JSON file to create/update")
    parser.add_argument("--keep", type=int, default=3, help="number of versions to keep (older ones are deleted)")
    args = parser.parse_args()

    api = HfApi(token=os.environ["HF_TOKEN"])
    api.create_repo(args.hf_repo, repo_type=args.hf_repo_type, private=False, exist_ok=True)

    short_name = args.box_name.split("/")[-1]
    path_in_repo = f"{short_name}/{args.version}/{args.provider}-{args.architecture}.box"
    url_prefix = "https://huggingface.co/" + ("datasets/" if args.hf_repo_type == "dataset" else "")
    url = f"{url_prefix}{args.hf_repo}/resolve/main/{path_in_repo}"

    print(f"Computing sha256 of {args.box}...", flush=True)
    checksum = sha256sum(args.box)

    print(f"Uploading {args.box} to {args.hf_repo}:{path_in_repo}...", flush=True)
    api.upload_file(
        path_or_fileobj=str(args.box),
        path_in_repo=path_in_repo,
        repo_id=args.hf_repo,
        repo_type=args.hf_repo_type,
        commit_message=f"Add {args.box_name} {args.version} ({args.provider})",
    )

    if args.catalog.exists():
        catalog = json.loads(args.catalog.read_text())
    else:
        catalog = {"name": args.box_name, "description": args.description, "versions": []}
    catalog["name"] = args.box_name
    if args.description:
        catalog["description"] = args.description

    versions = {v["version"]: v for v in catalog.get("versions", [])}
    entry = versions.setdefault(args.version, {"version": args.version, "providers": []})
    entry["providers"] = [
        p for p in entry["providers"]
        if not (p["name"] == args.provider and p.get("architecture") == args.architecture)
    ]
    entry["providers"].append({
        "name": args.provider,
        "url": url,
        "checksum_type": "sha256",
        "checksum": checksum,
        "architecture": args.architecture,
        "default_architecture": True,
    })

    ordered = sorted(versions.values(), key=lambda v: version_key(v["version"]), reverse=True)
    kept, removed = ordered[: args.keep], ordered[args.keep:]
    catalog["versions"] = kept

    for old in removed:
        folder = f"{short_name}/{old['version']}"
        print(f"Deleting old version {folder} from {args.hf_repo}...", flush=True)
        try:
            api.delete_folder(
                path_in_repo=folder,
                repo_id=args.hf_repo,
                repo_type=args.hf_repo_type,
                commit_message=f"Remove {args.box_name} {old['version']}",
            )
        except Exception as e:  # keep going: the catalog no longer references it anyway
            print(f"warning: could not delete {folder}: {e}", file=sys.stderr)
    if removed:
        # Deleted files stay in the git history (and keep using storage) until it is squashed.
        print(f"Squashing history of {args.hf_repo} to free storage...", flush=True)
        api.super_squash_history(repo_id=args.hf_repo, repo_type=args.hf_repo_type)

    args.catalog.parent.mkdir(parents=True, exist_ok=True)
    args.catalog.write_text(json.dumps(catalog, indent=2) + "\n")
    print(f"Catalog {args.catalog} updated: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
