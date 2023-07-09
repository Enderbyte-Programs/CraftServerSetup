#!/usr/bin/bash
#This program will be fixed, eventually

if [ "$EUID" -ne 0 ]; then
    echo "WARNING: You are not running as root. You will only uninstall locally."
    INSTALLDIR="$HOME/.local/bin"
    LIBDIR="$HOME/.local/lib/automcserver"
else
    INSTALLDIR="/usr/bin"
    LIBDIR="/usr/lib/automcserver"
fi

rm "$INSTALLDIR/automcserver"
rm "$INSTALLDIR/mcserver"
rm "$INSTALLDIR/amcs"

rm -rf "$LIBDIR"
echo "AutoMCServer is deleted"