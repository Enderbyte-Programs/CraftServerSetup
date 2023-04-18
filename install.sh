#!/usr/bin/sh
#This program installs automcserver. Run with --help for help or --local to install locally

if [ "$1" == "--remove" ] || [ "$1" == "-r" ]; then
    #Remove locally
    echo "Removing locally..."
    rm ~/.local/bin/automcserver 2>/dev/null
    rm ~/.local/bin/mcserver 2>/dev/null
    echo "Removing globally..."
    if [ "$EUID" -ne 0 ]
        then echo "WARNING: Root priviliges are required to uninstall globally"
    fi
    exit 0
fi

FILE=automcserver.py
if ! test -f "$FILE"; then
    #Download file
    if ! command -v wget &>/dev/null; then
        echo "wget is required to do a download install."
        exit 1
    fi
    if ! command -v gzip &>/dev/null; then
        echo "GZIP is required to do a download install"
        exit 1
    fi
    wget -q -O automcserver.py.gz http://enderbyteprograms.ddnsfree.com:10223/downloads/hosted/automcserver.py.gz
    gzip -df automcserver.py.gz
fi

if ! command -v python3 &>/dev/null; then
    echo "Please install Python3 before using this program"
    exit 1
fi

if ! command -v pip3 &>/dev/null; then
    echo "Please install python3-pip before using this program"
    exit 1
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
    echo " (no arguments) : Installs program globally (requires root)"
    exit 0
fi

if [ "$1" == "--local" ] || [ "$1" == "-l" ]; then
    cp $FILE ~/.local/bin/automcserver #Copy file
    chmod +x ~/.local/bin/automcserver # Allow execution
    if ! test -f "$HOME/.local/bin/mcserver"; then
        ln ~/.local/bin/automcserver ~/.local/bin/mcserver #Create link
    fi
    
    echo "Successfully installed AutoMcServer Locally"

else
    if [ "$EUID" -ne 0 ]
        then echo "Please run as root or run with --local argument"
        exit -1
    fi
    cp $FILE /usr/bin/automcserver # Copy file
    chmod +x /usr/bin/automcserver #Allow execution
    if ~ test -f "/usr/bin/mcserver"; then
        ln /usr/bin/automcserver /usr/bin/mcserver #Create link
    fi
    echo "Sucessfully installed Auto Minecraft Server"
fi
