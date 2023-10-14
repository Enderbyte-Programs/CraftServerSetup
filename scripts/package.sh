#!/usr/bin/bash
#This program is not meant to be used by common users

echo " ===> Creating standard package"
rm -rf *.xz *.amc dist *.log >/dev/null
tar --exclude='./analytics' --exclude='./assets/mc.ico' --exclude='./changelog' --exclude='./dev' --exclude='./deb' -cJf craftserversetup.tar.xz ./*
echo " ===> Creating Debian Package"
#Create deb directories. Ignore if they don't exist

rm -rf deb
rm craftserversetup.deb
mkdir deb
mkdir deb/DEBIAN
mkdir deb/usr
mkdir deb/usr/bin
mkdir -p deb/usr/lib/craftserversetup/tempdeb
mkdir -p deb/usr/share/applications
mkdir -p deb/usr/share/pixmaps

set -e
#From now on, errors should halt build

#Declare vars
DEBBINFOLDER="deb/usr/bin"
DEBLIBFOLDER="deb/usr/lib/craftserversetup"
DEBTEMPFOLDER="$DEBLIBFOLDER/tempdeb"
cp assets/control deb/DEBIAN
#Move control

#Process py file
cp src/craftserversetup.py deb/usr/bin/craftserversetup.py
sed '2,${/^#/d}' deb/usr/bin/craftserversetup.py >deb/usr/bin/craftserversetup.py.tmp
rm deb/usr/bin/craftserversetup.py
mv deb/usr/bin/craftserversetup.py.tmp deb/usr/bin/craftserversetup.py
grep -v -e '^[[:space:]]*$' deb/usr/bin/craftserversetup.py >deb/usr/bin/craftserversetup.py.tmp
rm deb/usr/bin/craftserversetup.py
mv deb/usr/bin/craftserversetup.py.tmp deb/usr/bin/craftserversetup.py
chmod +x deb/usr/bin/craftserversetup.py
mv deb/usr/bin/craftserversetup.py deb/usr/bin/craftserversetup

#Extract libraries

pushd lib >/dev/null
#Copy prebuilt python library
for file in *.xz
do
    tar -xf $file -C "../$DEBLIBFOLDER" #Extract library to custom library path
done
cp *.py "../$DEBLIBFOLDER" #Copy remaining custom librariespa
popd >/dev/null

#Move desktop and icon files
cp assets/mc.png deb/usr/share/pixmaps
cp assets/craftserversetup.desktop deb/usr/share/applications

#Move MIME into temporary directory
cp assets/mime.xml $DEBTEMPFOLDER

#Copy postinstall
cp scripts/debian/postinstall.sh deb/DEBIAN/postinst
chmod +x deb/DEBIAN/postinst

dpkg-deb --build deb craftserversetup.deb
