#!/usr/bin/bash
#This program will be fixed, eventually

if [ "$EUID" -ne 0 ]; then
    echo "WARNING: You are not running as root. You are only uninstalling locally"
    INSTALLDIR="$HOME/.local/bin"
    LIBDIR="$HOME/.local/lib/craftserversetup"
    ICONDIR="$HOME/.local/share/icons"
    SHORTCUTDIR="$HOME/.local/share/applications"
else
    INSTALLDIR="/usr/bin"
    LIBDIR="/usr/lib/craftserversetup"
    ICONDIR="/usr/share/pixmaps"
    SHORTCUTDIR="/usr/share/applications"
fi

rm "$INSTALLDIR/craftserversetup"
rm "$INSTALLDIR/mcserver"
rm "$INSTALLDIR/crss"

rm -rf "$LIBDIR"
rm $ICONDIR/craftserversetup.png
rm $SHORTCUTDIR/craftserversetup.desktop
echo "craftserversetup is deleted"