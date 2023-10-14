#!/usr/bin/bash

#This program finishes the installer.

#TODO: Install MIME type
FILEREGFILE="$HOME/.config/mimeapps.list"
MIMEDIR="$HOME/.local/share/mime/packages"

if [ -f $FILEREGFILE ]; then
    if ! grep -q "minecraft-server" "$FILEREGFILE"; then
        echo "application/minecraft-server=craftserversetup.desktop" >> $FILEREGFILE
    fi
fi

if [ ! -d $MIMEDIR ]; then
    mkdir -p $MIMEDIR
fi
if [ ! -f $MIMEDIR/craftserversetup.xml ]; then
    cp /usr/lib/craftserversetup/tempdeb $MIMEDIR/craftserversetup.xml
fi

rm -rf /usr/lib/craftserversetup/tempdeb
