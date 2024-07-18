# Craft Server Setup
## The best way to set up a Minecraft Server on your computer

## Setup and Installation

## WINDOWS

The Windows edition uses an installer. Follow the steps in the installer. All dependencies are included.

You may have to dismiss warnings of uncommon programs or even malware from Windows. Please dismiss them as they are false alarms. If this program contains a virus that I have willingly included, you may sue me for a million dollars.

## Linux

### Installing from release tar.xz

- Download craftserversetup.tar.xz from the latest release

- Unzip the tar.xz to a directory with `tar -xf craftserversetup.tar.xz`

- Open a terminal in that directory `cd craftserversetup`

- Run the command `./installer`

- This will install it locally. To install it for everyone, run `sudo ./installer`

- To remove it, run `./installer uninstall`

- If for some reason the installer is not executable, run `python3 installer`


### Building from source

- Clone the repository with `git clone <url>`

- Install sbuild-dofile from https://github.com/Enderbyte-Programs/sbuild-dofile

- In the repo directory, run `sbuild einstall`

- This will install it

Run the following script with or without root (depending on where you want CRSS installed):

```bash
set -e
if [ -d "crss-build" ];then
    rm -rf crss-build
fi

mkdir crss-build
pushd crss-build
mkdir crss
mkdir build
git clone https://github.com/Enderbyte-Programs/CraftServerSetup ./crss
git clone https://github.com/Enderbyte-Programs/sbuild-dofile ./build

pushd build
python3 do.py
popd

pushd crss
../build/build/do
popd
popd
echo "Installation finished with no errors."
```