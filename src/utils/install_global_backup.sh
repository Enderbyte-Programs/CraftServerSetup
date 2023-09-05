#!/usr/bin/bash
#DANGER! This is incredibly dangerous
#$1 is backup file to load
BACKUPDIR="$HOME/.local/share/crss_backup"
SYSDIR="$HOME/.local/share/mcserver"
if [ ! -d $BACKUPDIR ]; then
    mkdir -p $BACKUPDIR
fi
if [ ! -f $1 ]; then
    
    exit 1
fi
if [ -d $BACKUPDIR/tempbk ]; then
    rm -rf $BACKUPDIR/tempbk
fi

mkdir $BACKUPDIR/tempbk
cp -r $SYSDIR/* $BACKUPDIR/tempbk
{
    rm -rf $SYSDIR
    mkdir $SYSDIR
    tar -xf $1 -C $SYSDIR --overwrite
    rm -rf $BACKUPDIR/tempbk
    exit 0
} || {
    #Restore old version
    mkdir $SYSDIR
    cp -r $BACKUPDIR/tempbk/* $SYSDIR
    rm -rf $BACKUPDIR/tempbk
    exit 1
}