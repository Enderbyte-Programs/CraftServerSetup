# automcserver
## The best way to set up a Minecraft server on Linux

## Setup and Installation

NOTICE: We are currently overhauling the build system to make it more controlled. Please report any issues you have upgrading to AMCS 0.7

First, download automcserver.tar.xz or download the github repo. Next, extract it into a build directory. In this directory you should have a symlink called "install." However, this is likely not preserved if you did a zip download rather than a release.

Open a terminal to the source tree. Run `./install` or `bash scripts/install.sh` if the first command does not work. The first time you build the program it will take some time to build some libraries. However, subsequent builds will be faster.

Next, run `automcserver`. The program will do the remainder of the setup

## About The Folders

src: Source code

src/utils: Utils scripts

scripts: Build system scripts

lib: Special library versions to increase control and decrease dependancy