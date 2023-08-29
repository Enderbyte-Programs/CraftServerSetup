#!/usr/bin/bash
#$1 is backup name
set -e
BACKUPDIR="$HOME/.local/share/amcs_backup"
SYSDIR="$HOME/.local/share/mcserver"
if [ ! -d $BACKUPDIR ]; then
    mkdir -p $BACKUPDIR
fi

pushd $SYSDIR >/dev/null
tar -cJvf "${BACKUPDIR}/${1}.tar.xz" .
popd >/dev/null