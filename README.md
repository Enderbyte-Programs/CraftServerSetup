# automcserver
## The best way to set up a Minecraft server on Linux

## IMPORTANT NOTICE

**AS IT TURNS OUT, THIS NAME IS VERY COMMON. THIS IS A COMPLETELY UNIQUE PROGRAM MADE IN 2022 AND IS THE MOST ADVANCED OF ITS NAME.**

## Setup and Installation

First, download automcserver.tar.xz or download the github repo. Next, extract it into a build directory. In this directory you should have a symlink called "install." However, this is likely not preserved if you did a zip download rather than a release.

Open a terminal to the source tree. Run `./install` or `bash scripts/install.sh` if the first command does not work. The first time you build the program it will take some time to build some libraries. However, subsequent builds will be faster.

Next, run `automcserver`. The program will do the remainder of the setup

## About The Folders

src: Source code

src/utils: Utils scripts

scripts: Build system scripts

lib: Special library versions to increase control and decrease dependancy

## My TODO List

0.12.1 - Spigot upgrades

0.12.2 - New installer and improved exceptions

0.12.3 - Analytics

0.12.4 - Proprietarization

0.13 - Backups

0.14 - Bukkit classic support