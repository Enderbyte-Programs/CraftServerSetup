#!/usr/bin/bash
#This program will be fixed, eventually

if [ "$EUID" -ne 0 ]; then
    echo "WARNING: You are not running as root. You will only uninstall locally."
    INSTALLDIR="$HOME/.local/bin"
    LIBDIR="$HOME/.local/lib/craftserversetup"
else
    INSTALLDIR="/usr/bin"
    LIBDIR="/usr/lib/craftserversetup"
fi

rm "$INSTALLDIR/craftserversetup"
rm "$INSTALLDIR/mcserver"
rm "$INSTALLDIR/amcs"

rm -rf "$LIBDIR"
echo "craftserversetup is deleted"