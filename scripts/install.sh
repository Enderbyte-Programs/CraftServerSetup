#!/usr/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
FILEREGFILE="$HOME/.config/mimeapps.list"
MIMEDIR="$HOME/.local/share/mime/packages"

#Check program requirements
set -e
echo "Checking for programs..."
if ! command -v python3 &> /dev/null
then
    echo "Python3 is required to use this program"
    exit 1
fi
if ! command -v tar &> /dev/null
then
    echo "tar is required to use this program"
    exit 1
fi
if ! command -v xz &> /dev/null
then
    echo "xz is required to use this"
    exit 1
fi
if ! command -v sed &> /dev/null
then
    echo "sed is required to build this program"
    exit 1
fi
if ! command -v grep &> /dev/null
then
    echo "grep is required to build this program"
    exit 1
fi
if ! command -v java &> /dev/null
then
    echo "WARNING: You should probably have java if you want to set up a Minecraft server"
fi

#Set up folders
echo "Setting up..."
if [ "$EUID" -ne 0 ]; then
    echo "WARNING: You are not running as root. Program will be installed locally."
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
APPDATADIR="$HOME/.local/share/mcserver"
if [ ! -d "$APPDATADIR" ]; then
    mkdir -p "$APPDATADIR"
fi
if [ ! -d "$LIBDIR" ]; then
    mkdir -p "$LIBDIR"
fi
if [ ! -d "$INSTALLDIR" ]; then
    mkdir -p "$INSTALLDIR"
    if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
        echo ""
    else
        echo "WARNING: Local bin directory is not on PATH"
    fi

fi

echo "Building"
if [ -d "dist" ]; then
    echo "WARNING: dist directory found. Deleting now."
    rm -rf dist # Clean dist directory
fi
mkdir dist
#Copy code and add exec permissions
cp src/craftserversetup.py dist/craftserversetup.py
sed '2,${/^#/d}' dist/craftserversetup.py >dist/craftserversetup.py.tmp
#grep -o '^[^#]*' dist/craftserversetup.py >dist/craftserversetup.py.tmp
rm dist/craftserversetup.py
mv dist/craftserversetup.py.tmp dist/craftserversetup.py
grep -v -e '^[[:space:]]*$' dist/craftserversetup.py >dist/craftserversetup.py.tmp
rm dist/craftserversetup.py
mv dist/craftserversetup.py.tmp dist/craftserversetup.py
chmod +x dist/craftserversetup.py
mv dist/craftserversetup.py dist/craftserversetup
echo "Installing"
cp dist/craftserversetup "$INSTALLDIR/craftserversetup"

ln -sf "$INSTALLDIR/craftserversetup" "$INSTALLDIR/mcserver"
ln -sf "$INSTALLDIR/craftserversetup" "$INSTALLDIR/crss"

echo "Installing libraries: "
pushd lib >/dev/null
#Copy prebuilt python library
for file in *.xz
do
    echo "      ${file}"
    tar -xf $file -C $LIBDIR #Extract library to custom library path
done
cp *.py $LIBDIR #Copy remaining custom librariespa
popd >/dev/null

echo "Creating Shortcut"
if [ ! -d $ICONDIR ]; then
    mkdir -p $ICONDIR
fi
if [ ! -d $SHORTCUTDIR ]; then
    mkdir -p $SHORTCUTDIR
fi
cp assets/mc.png $ICONDIR/craftserversetup.png
cp assets/craftserversetup.desktop "${SHORTCUTDIR}/craftserversetup.desktop"
sed -i "s@}@${ICONDIR}@g" "${SHORTCUTDIR}/craftserversetup.desktop"
#Replace home path in shortcut file

#Register mime type
if [ ! -d $MIMEDIR ]; then
    mkdir -p $MIMEDIR
fi
if [ ! -f $MIMEDIR/craftserversetup.xml ]; then
    cp assets/mime.xml $MIMEDIR/craftserversetup.xml
fi

#Create file association
if [ -f $FILEREGFILE ]; then
    if ! grep -q "minecraft-server" "$FILEREGFILE"; then
        echo "application/minecraft-server=craftserversetup.desktop" >> $FILEREGFILE
    fi
fi

cp doc/craftserversetup.epdoc $LIBDIR
rm -rf dist
printf "${GREEN}CraftServerSetup installed successfully!${NC}\n"