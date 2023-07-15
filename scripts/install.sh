#!/usr/bin/bash

#Check program requirements
set -e
echo "Checking for programs..."
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
    echo "WARNING: gcc is required to build a portion of a library that this program depends on. Program failure will likely happen now. On some systems you can ignore this."
fi

#Set up folders
echo "Setting up..."
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

echo "Installing"
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
        echo "ERROR: libyaml build failed with exit code $RES2."
        exit 2
    fi
    cd build
    cp -r ./lib*/* "$LIBDIR"
else
    echo "libyaml is already built, skipping to save time"
fi

popd >/dev/null
rm -rf lib/PyYAML-6.0

echo "Program installed successfully!"