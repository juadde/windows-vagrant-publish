# Windows for vagrant (libvirt) build

This repository automates windows builds for Vagrant.

Since HCP Vagrant Registry has stopped accepting new boxes (it is being shut down), boxes are now hosted in an
S3-compatible bucket (Cloudflare R2, Oracle Cloud Object Storage, Backblaze B2, ...). A Vagrant catalog file (box
metadata, with versions and sha256 checksums) is stored next to the boxes, so `vagrant box outdated` and
`vagrant box update` work as with a registry.

It is based on [rgl/windows-vagrant](https://github.com/rgl/windows-vagrant) and uses the same build process.

The only difference is that the locales are set to fr-FR (only the input methods, not the UI language).
The builds are based on the ```UEFI``` variants, with ```libvirt``` provider.

 
Timezone still need to be configured through your ```Vagrantfile``` with this kind of command:
```powershell
tzutil /s "Romance Standard Time"
```

## Usage

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "kppqju77/windows-11-fr-input"
  config.vm.box_url = "<S3_PUBLIC_URL>/windows-11-fr-input.json"
end
```

## Publishing setup

Create a bucket with public read access (e.g. an R2 bucket with a custom domain or its `r2.dev` URL), and an S3 API
key with write access to it. Then, in the GitHub repository settings (*Secrets and variables → Actions*), add:

| Kind     | Name                   | Example                                          |
|----------|------------------------|--------------------------------------------------|
| secret   | `S3_ACCESS_KEY_ID`     |                                                  |
| secret   | `S3_SECRET_ACCESS_KEY` |                                                  |
| variable | `S3_ENDPOINT_URL`      | `https://<account-id>.r2.cloudflarestorage.com`  |
| variable | `S3_BUCKET`            | `vagrant-boxes`                                  |
| variable | `S3_PUBLIC_URL`        | `https://pub-xxxx.r2.dev`                        |
| variable | `S3_REGION`            | optional, defaults to `auto`                     |
| variable | `BOX_KEEP`             | optional, number of versions kept, defaults to 1 |
| variable | `BOX_PRUNE_FIRST`      | optional, `true` deletes old versions before uploading (tight quotas) |

A new version is built every two weeks. The version numbering is based on the date and time the build has been created, and the run number of the CI/CD.

## Windows 11

Status of the Windows 11 build:

[![Build and publish Windows 11 (UEFI) FR input](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-11-fr-input.yml/badge.svg)](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-11-fr-input.yml)

## Windows 2025

Status of the Windows 2025 build:

[![Build and publish Windows 2025 (UEFI) FR input](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-2025-fr-input.yml/badge.svg)](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-2025-fr-input.yml)
