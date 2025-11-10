# Craft Server Setup
## A CLI Minecraft Server Manager

## Setup and Installation

## WINDOWS

The Windows edition uses an installer. Follow the steps in the installer. All dependencies are included.

You may have to dismiss warnings of uncommon programs or even malware from Windows. Please dismiss them as they are false alarms. 

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

- In the repo directory, run `sbuild install`

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

## Other Important Things

ATTENTION - If you use an old version of this software, it might ask you for a "product key." This system has been retired, so it may confuse you. Please paste the code `4p6jgtnatqj5svb4` if it asks you for one.

## Integrating Third Party Software

If you would like to make your application work with CRSS, here is how to do so

### Server automatic restarts

You can control whether or not CRSS automatically restarts a server by writing a file in the server's root directory named `autorestart`

** Requirements **
- CRSS v1.53 or newer
- User must set Autorestart Source to allow external file

This `autorestart` must contain some certain recognized words, in any case, seperated by a space. Recognized words include:
- `never` - Never automatically restart the server (May not be used with safe/unsafe) *Optional - if neither safe nor unsafe are provided, this is the default behaviour*
- `safe` - Automatically restart the server if it exited safely (may not be used with never)
- `unsafe` - Automatically restart the server if it did not exit safely. (may not be used with never)
- `disposable` - "Consume" this autorestart file so that it may be only read once. (may not be used with persistent) *Optional - if persistent is not provided, this is the default behaviour*
- `persistent` - Keep this file (do not delete it when it is read)

**For example**

`safe persistent` - Autorestart the server if it doesn't crash. This file may be used multiple times.
`safe unsafe` - Autorestart the server all the time, no matter what.