#!/usr/bin/bash

set -e
if [ -d "/tmp/amcsupdate" ]; then
    rm -rf /tmp/amcsupdate
fi
mkdir /tmp/amcsupdate

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
if ! command -v git &> /dev/null
then
    echo "git is required to update."
    exit 1
fi

pushd /tmp/amcsupdate
git clone https://github.com/Enderbyte-Programs/automcserver/
cd automcserver
bash scripts/install.sh
popd
echo "AutoMCServer updated successfully. Restart it with the amcs command."