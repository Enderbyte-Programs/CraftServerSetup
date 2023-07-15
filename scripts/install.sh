#!/usr/bin/bash

#Check program requirements
set -e
if ! command -v python3 &> /dev/null
then
    echo "Python3 is required to use this program"
    exit 1
fi
if ! command -v unzip &> /dev/null
then
    echo "unzip is required to use this"
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
    echo "WARNING: gcc is required to build a portion of a library that this program depends on. Program failure will likely happen now. On some systems you can ignore this."
fi

#Set up folders

if [ "$EUID" -ne 0 ]; then
    echo "WARNING: You are not running as root. Program will be installed locally."
    INSTALLDIR="$HOME/.local/bin"
    LIBDIR="$HOME/.local/lib/automcserver"
else
    INSTALLDIR="/usr/bin"
    LIBDIR="/usr/lib/automcserver"
fi

if [ ! -d "$LIBDIR" ]; then
    mkdir -p "$LIBDIR"
fi

#Copy code and add exec permissions
cp src/automcserver.py "$INSTALLDIR/automcserver"
chmod +x "$INSTALLDIR/automcserver"
if [ ! -L "$INSTALLDIR/mcserver" ]; then
    ln -s "$INSTALLDIR/automcserver" "$INSTALLDIR/mcserver"
fi
if [ ! -L "$INSTALLDIR/amcs" ]; then
    ln -s "$INSTALLDIR/automcserver" "$INSTALLDIR/amcs"
fi

#Copy prebuild util scripts
cp -r src/utils "$LIBDIR"
chmod -R +rx "$LIBDIR/utils" 

#Copy prebuilt python library
for file in lib/*.whl
do
    unzip -q -o "$file" -d "$LIBDIR" #Extract library to custom library path
done

#Build unbuilt library
if [ ! -d "$LIBDIR/yaml" ]; then
    pushd lib

    tar -xf PyYAML-6.0.tar.gz
    cd PyYAML-6.0
    make -s
    python3 setup.py build -q
    cd build
    cp -r ./lib*/* "$LIBDIR"

    popd
else
    echo "libyaml is already built, skipping to save time"
fi

rm -rf lib/PyYAML-6.0

echo "Program installed successfully!"