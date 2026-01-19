# Windows for vagrant (libvirt) build

This repository automates windows builds in the [Kppqju77](https://portal.cloud.hashicorp.com/vagrant/discover/kppqju77) Vagrant registry.

It is based on [rgl/windows-vagrant](https://github.com/rgl/windows-vagrant) and uses the same build process.

The only difference is that the locales are set to fr-FR (only the input methods, not the UI language).
The builds are based on the ```UEFI``` variants, with ```libvirt``` provider.

 
Timezone still need to be configured through your ```Vagrantfile``` with this kind of command:
```powershell
tzutil /s "Romance Standard Time"
```

A new version is built every two weeks. The version numbering is based on the date and time the build has been created.

## Windows 11

Status of the [Windows 11 build](https://portal.cloud.hashicorp.com/vagrant/discover/Kppqju77/windows-11-fr-input):

[![Build and publish Windows 11 (UEFI) FR input](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-11-fr-input.yml/badge.svg)](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-11-fr-input.yml)

## Windows 2025

Status of the [Windows 2025 build](https://portal.cloud.hashicorp.com/vagrant/discover/Kppqju77/windows-2025-fr-input):

[![Build and publish Windows 2025 (UEFI) FR input](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-2025-fr-input.yml/badge.svg)](https://github.com/juadde/windows-vagrant-publish/actions/workflows/windows-2025-fr-input.yml)
