#!/usr/bin/bash

echo "--> Universal Installer for CraftServerSetup"
set -e
if ! command -v curl &> /dev/null
then
    echo "Curl is required to execute the universal installer"
    exit 1
fi
#curl -LsI -o /tmp/crssuniurl -w %{url_effective} https://github.com/Enderbyte-Programs/CraftServerSetup/releases/latest
echo "--> Resolving version"
url=$(curl https://github.com/Enderbyte-Programs/CraftServerSetup/releases/latest -s -L -I -o /dev/null -w '%{url_effective}')

endver=$(echo $url | rev | cut -d/ -f1 | rev)
endurl="https://github.com/Enderbyte-Programs/CraftServerSetup/releases/download/${endver}/craftserversetup.tar.xz"
#echo $endurl
echo "--> Downloading file"
curl --progress-bar -L --output /tmp/crssuni.tar.xz $endurl

echo "--> Extracting package"
cd /tmp
mkdir -p crssuni
tar -xf crssuni.tar.xz -C crssuni

echo "--> Installing"
cd crssuni
chmod +x ./installer
./installer

echo -e \
"======================\n\
Installation complete\n\
Run the crss command\n\
======================\n"