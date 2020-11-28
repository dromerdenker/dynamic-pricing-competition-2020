#!/bin/bash
[ -f secrets.vault ] && echo "secrets.vault found... loading" || echo "ERROR: Copy secrets.vault_example into secrets.vault with your credentials."
source secrets.vault

# rule is to create a folder of the upload date, and therein put the python code
TODAY=$(date "+%Y-%m-%d")

# open FTP connection
# change the last nlist to what you want to know :-)
ftp -inv $FTP_SERVER <<EOF
user $FTP_LOGIN $FTP_PASSWORD
bell
nlist /
nlist /$TODAY
bye
EOF

# TODO: this is clunky. I have no better way though.
