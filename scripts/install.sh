#!/usr/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

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
if ! command -v gzip &> /dev/null
then
    echo "gz is required to use this"
    exit 1
fi
if ! command -v make &> /dev/null
then
    echo "WARNING: GNUMake is required to build a library that this program relies on. "
fi
if ! command -v java &> /dev/null
then
    echo "WARNING: You should probably have java if you want to set up a Minecraft server"
fi
if ! command -v gcc &> /dev/null
then
    echo "WARNING: gcc is required to build a portion of a library that this program depends on."
fi

#Set up folders
echo "Setting up..."
if [ "$EUID" -ne 0 ]; then
    echo "WARNING: You are not running as root. Program will be installed locally."
    INSTALLDIR="$HOME/.local/bin"
    LIBDIR="$HOME/.local/lib/craftserversetup"
else
    INSTALLDIR="/usr/bin"
    LIBDIR="/usr/lib/craftserversetup"
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

#Copy prebuild util scripts
echo "Copying scripts"
cp -r src/utils "$LIBDIR"
chmod -R +rx "$LIBDIR/utils" 

echo "Installing libraries: "
pushd lib >/dev/null
#Copy prebuilt python library
for file in *.xz
do
    echo "      ${file}"
    tar -xf $file -C $LIBDIR #Extract library to custom library path
done

echo "Building libyaml"
#Build unbuilt library
if [ ! -d "$LIBDIR/yaml" ]; then
    tar -xf PyYAML-6.0.tar.gz
    cd PyYAML-6.0
    set +e #Disable crashing
    make >/dev/null
    RES1=$?
    python3 setup.py build >/dev/null
    RES2=$?
    set -e
    if [ "$RES1" -ne 0 ] && [ "$RES2" -ne 0 ]; then
        printf "${RED}ERROR: libyaml build failed with exit code $RES2.${NC}\n"
        exit 2
    fi
    cd build
    cp -r ./lib*/* "$LIBDIR"
else
    echo "libyaml is already built, skipping to save time"
fi

popd >/dev/null
rm -rf lib/PyYAML-6.0

printf "${GREEN}Program installed successfully!${NC}\n"