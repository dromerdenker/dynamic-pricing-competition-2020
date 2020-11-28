#!/bin/bash
[ -f secrets.vault ] && echo "secrets.vault found... loading" || echo "ERROR: Copy secrets.vault_example into secrets.vault with your credentials."
source secrets.vault

# rule is to create a folder of the upload date, and therein put the python code
TODAY=$(date "+%Y-%m-%d")

# open FTP connection
ftp -inv $FTP_SERVER <<EOF
user $FTP_LOGIN $FTP_PASSWORD
bell
mkdir $TODAY
cd $TODAY
mput requirements.txt
lcd src
mput *.py
ls
bye
EOF
