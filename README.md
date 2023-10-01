# Craft Server Setup
## The best way to set up a Minecraft Server on your computer

## Setup and Installation

## WINDOWS

The Windows edition uses an installer. Follow the steps in the installer. All dependencies are included.

You may have to dismiss warnings of uncommon programs or even malware from Windows. Please dismiss them as they are false alarms. If this program contains a virus that I have willingly included, you may sue me for a million dollars.

## Linux

### Dependencies not included

These should not be an issues as almost everyone has these programs. CraftServerSetup comes bundled with all required Python libraries

python3, xz, tar, coreutils, sed, grep

### Downloading

First, download craftserversetup.tar.xz or download the github repo. Next, extract it into a build directory with the command: `mkdir crss_build;tar -xf craftserversetup.tar.xz -C crss_build;cd crss_build`. Now you are in the source tree.

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

## BECOME A BETA TESTER!

As CraftServerSetup reaches a milestone one (and thus the 1.0 update), I need some helpers to help me find the last bugs in this program so I can have a nice stable 1.0. To become a beta tester, please send me an email at enderbyte09@gmail.com or message me on discord @enderbyte09. 

As a beta tester, you will need to just use the program, set servers up, screw around, do as much as you want. If you find any bugs, all you need to do is report in the Issues section of this GitHub page or send me an email or Discord.

If you join the Beta Testing program, you will recieve the following rewards:

1. Your name in the credits page of this program

2. A free product key to this software (so you don't have to see any ads)

3. One free infinite advertisement that will be put on the Enderbyte Programs ad network and displayed to all unupgraded CraftServerSetup users

## The future

MangyCat has suggested that I convert this to a web ui. To do this first, the backend must be detached from the frontend

## Product Keys and Ads

As of 0.12.4 this program is semiproprietary. The code remains open source but is commercial in nature. A product key costs $2. If you don't want to get a product key, you have a 20% chance of seeing an ad every time you do something from the main menu. **If anybody would like to advertise on my ads system, please send me an email at enderbyte09@gmail.com**

## My TODO List

Fix as many bugs as possible