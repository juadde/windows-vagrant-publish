# Windows for vagrant (libvirt) build

This repository automates windows builds for Vagrant.

Since HCP Vagrant Registry has stopped accepting new boxes (it is being shut down), boxes are now hosted for free on
[Hugging Face](https://huggingface.co) and the Vagrant catalog files (box metadata, with versions and checksums) are
served by GitHub Pages from the [`docs`](docs) directory. Only the 3 latest versions of each box are kept.

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
  config.vm.box_url = "https://juadde.github.io/windows-vagrant-publish/windows-11-fr-input.json"
end
```

Or directly: `vagrant box add https://juadde.github.io/windows-vagrant-publish/windows-11-fr-input.json`.
`vagrant box outdated` and `vagrant box update` work as with a registry.

## Publishing setup

1. Create a [Hugging Face](https://huggingface.co) account and a **write** access token.
2. In the GitHub repository settings, add:
   - the secret `HF_TOKEN` (the Hugging Face token);
   - the variable `HF_REPO` (e.g. `<hf-user>/windows-vagrant`, created automatically as a public repository).
3. Enable GitHub Pages: *Settings → Pages → Deploy from a branch → `main` / `/docs`*.

A new version is built every two weeks. The version numbering is based on the date and time the build has been created, and the run number of the CI/CD.

## Windows 11

Status of the Windows 11 build ([catalog](https://juadde.github.io/windows-vagrant-publish/windows-11-fr-input.json)):

[![Build and publish Windows 11 (UEFI) FR input](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-11-fr-input.yml/badge.svg)](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-11-fr-input.yml)

## Windows 2025

Status of the Windows 2025 build ([catalog](https://juadde.github.io/windows-vagrant-publish/windows-2025-fr-input.json)):

[![Build and publish Windows 2025 (UEFI) FR input](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-2025-fr-input.yml/badge.svg)](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-2025-fr-input.yml)
