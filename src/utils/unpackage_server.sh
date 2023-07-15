#!/usr/bin/bash
#$1 is infile
#$2 is out directory
# RETURN CODES
# 0: Everything worked well
# 7: File read/write errors
# 8: Missing program

if ! command -v tar &> /dev/null
then
    exit 8
fi
if ! command -v xz &> /dev/null
then
    exit 8
fi
mkdir -p "$2"
pushd "$2" >/dev/null
tar -xf "$1"
WL=$?
popd >/dev/null
if [ $WL -ne 0]; then
    exit 7
fi
exit 0