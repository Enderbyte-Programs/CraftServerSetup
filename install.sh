#!/usr/bin/sh
#This program installs and removes automcserver. Run with --help for help or --local to install locally

FILE=automcserver.py
APPDATAFOLDER=~/.local/share/mcserver
LOCAL_INSFILE=~/.local/bin/automcserver
LOCAL_INSLNK=~/.local/bin/mcserver
INSLNK=/bin/mcserver
INSFILE=/bin/automcserver
DNURL=https://github.com/Enderbyte-Programs/automcserver/raw/main/automcserver.py

if [ "$1" == "--remove" ] || [ "$1" == "-r" ]; then
    #Remove locally
    echo "Removing locally..."
    rm $LOCAL_INSFILE 2>/dev/null
    rm $LOCAL_INSLNK 2>/dev/null
    echo "Removing globally..."
    if [ "$EUID" -ne 0 ]
        then echo "WARNING: Root priviliges are required to uninstall globally"
    else
        rm $INSLNK 2>/dev/null
        rm $INSFILE 2>/dev/null
    fi
    exit 0
fi
if [ "$1" == "--clear" ] || [ "$1" == "-c" ]; then
    echo "Clearing appdata"
    du -hs $APPDATAFOLDER
    #Print size info
    rm -rf $APPDATAFOLDER
    echo "Appdata is cleared"
    exit 0
fi

if ! test -f "$FILE"; then
    #Download file
    if ! command -v wget &>/dev/null; then
        echo "wget is required to do a download install."
        exit -1
    fi

    wget -q -O $FILE $DNURL
fi

if ! command -v python3 &>/dev/null; then
    echo "Please install Python3 before using this program"
    exit -1
fi

if ! command -v pip3 &>/dev/null; then
    echo "Please install python3-pip before using this program"
    exit -1
fi
if ! command -v java &>/dev/null; then
    read -p "WARNING: You need java to run a Minecraft server. Are you sure you want to go ahead with the install?" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]
        then
            exit 1
    fi
fi

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Auto Minecraft Server Installer by Enderbyte Programs (c) 2023"
    echo "Usage: install.sh [Arguments]"
    echo "-h --help :       Displays this help menu"
    echo "-l --local :      Installs program locally (doesn't need root)"
    echo "-r --remove :     Removes program both globally and locally"
    echo "-c --clear :      Clear appdata and servers for automcserver"
    echo " (no arguments) : Installs program globally (requires root)"
    exit 0
fi

if [ "$1" == "--local" ] || [ "$1" == "-l" ]; then
    cp $FILE $LOCAL_INSFILE #Copy file
    chmod +x $LOCAL_INSFILE # Allow execution
    if ! test -f "$HOME/.local/bin/mcserver"; then
        ln $LOCAL_INSFILE $LOCAL_INSLNK #Create link
    fi
    
    echo "Successfully installed AutoMcServer Locally"

else
    if [ "$EUID" -ne 0 ]
        then echo "Please run as root or run with --local argument"
        exit -1
    fi
    cp $FILE $INSFILE # Copy file
    chmod +x $INSFILE #Allow execution
    if ~ test -f $INSLNK; then
        ln $INSFILE $INSLNK #Create link
    fi
    echo "Sucessfully installed Auto Minecraft Server"
fi
