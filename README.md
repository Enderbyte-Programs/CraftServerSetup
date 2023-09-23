# Craft Server Setup
## The best way to set up a Minecraft Server on your computer

## Setup and Installation

## WINDOWS

The Windows edition uses an installer. Follow the steps in the installer. All dependencies are included.

## Linux

### Dependencies not included

These should not be an issues as almost everyone has these programs. CraftServerSetup comes bundled with all required Python libraries

python3, xz, tar, coreutils, sed, grep

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

analytics: The server side of the telemetry server (shown for transparency)

assets: desktop files and icon files

## My Thoughts for Update 1.0

I believe that CraftServerSetup is nearing completion, if not at least a major milestone. This major milestone is the 1.0 update which is coming soon. There are a few nyi(). My goal is to get rid of the not yet implemented error by 0.16.
The next updates will get in the last few things I want to have. After this, I will do a lot of things to look for bugs, fix as many as I can and that will be 1.0!

## Product Keys and Ads

As of 0.12.4 this program is semiproprietary. The code remains open source but is commercial in nature. A product key costs $2. If you don't want to get a product key, you have a 20% chance of seeing an ad every time you do something from the main menu. **If anybody would like to advertise on my ads system, please send me an email at enderbyte09@gmail.com**

## My TODO List

0.17 - Operator manager and bans manager.

0.18 - Help menu with some docs. Also include new user tutorials.

1.0-rc - As many bug fixes as I can

1.0 - GOAL!