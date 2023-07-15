#!/usr/bin/bash
#$1 is package directory
#$2 is output file
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
pushd "$1" >/dev/null
tar -cJf "$2" ./* > /dev/null 2&>1
WL=$?
popd >/dev/null
if [ $WL -ne 0]; then
    exit 7
fi
exit 0