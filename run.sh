#!/usr/bin/bash

#sftp automcserver.py sftp://jordan@raspberrypi/home/jordan/hosted
cp automcserver.py amc_n.py
sed -i '/^[[:blank:]]*#/d;s/#.*//' amc_n.py
sed -i '/^[[:space:]]*$/d' amc_n.py
gzip -k9 amc_n.py
scp amc_n.py.gz jordan@raspberrypi:/home/jordan/hosted/automcserver.py.gz
rm amc_n.py.gz
rm amc_n.py
bash install.sh -l
automcserver
