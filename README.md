# Craft Server Setup
## The best way to set up a Minecraft server on Linux

## Setup and Installation

### Dependencies

STRONG: python3, gzip, xz, tar, coreutils

WEAK: gcc, make, java

### Downloading

First, download craftserversetup.tar.xz or download the github repo. Next, extract it into a build directory with the command: `mkdir crss_build;tar -xf craftserversetup.tar.xz -C crss_build;cd build`. Now you are in the source tree.

Now here there are two install methods

### 1. Interactive installation (best for humans)

In your terminal, execute `python3 install.py` or run it in a terminal. You will see a list of commands. Press "I" for Install. If it succeeds, the top message will say good. If it says bad, check recent.log

Next, run `crss`. The program will do the remainder of the setup

### 2. Non-interactive installation

In your terminal, execute `bash scripts/install.sh`. This will install automcserver verbosely

Next, run `crss`. The program will do the remainder of the setup

## About The Folders

src: Source code

src/utils: Utils scripts

scripts: Build system scripts

lib: Special library versions to increase control and decrease dependancy

## My TODO List

0.13 - Backups, Further proprietarization

0.13.1 - Fix textview()

0.14 - Removal of shell dependency (Preparation for Windows environment)

0.15 - Classic Bukkit support

(unscheduled procrastination) - Windows support