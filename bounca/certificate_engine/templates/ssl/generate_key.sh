#!/usr/bin/env bash -e 

cd "$(dirname "$0")"

passphrase_out=""
if [ -e "passphrase_out.txt" ]
then
    passphrase_out="-passout file:passphrase_out.txt"
fi

openssl genrsa -aes256 -out ./private/{{ key_name }}.key.pem $passphrase_out {{ key_length }}

chmod 400 ./private/{{ key_name }}.key.pem


exit 0
