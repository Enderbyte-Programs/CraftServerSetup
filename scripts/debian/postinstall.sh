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
    cp /usr/lib/craftserversetup/tempdeb/mime.xml $MIMEDIR/craftserversetup.xml
fi

if [ ! -d "~/.local/share/mcserver/assets" ]; then
    mkdir -p "~/.local/share/mcserver/assets"
fi
cp /usr/lib/craftserversetup/tempdeb/* "~/.local/share/mcserver/assets" #Copy docs and license and such

rm -rf /usr/lib/craftserversetup/tempdeb

#Create symlinks
INSTALLDIR="/usr/bin"
ln -sf "$INSTALLDIR/craftserversetup" "$INSTALLDIR/mcserver"
ln -sf "$INSTALLDIR/craftserversetup" "$INSTALLDIR/crss"
