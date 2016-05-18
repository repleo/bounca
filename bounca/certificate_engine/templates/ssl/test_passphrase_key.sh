#!/bin/bash -e 

cd "$(dirname "$0")"

passphrase_in=""
if [ -e "./passphrase_in.txt" ]
then
    passphrase_in="-passin file:./passphrase_in.txt"
fi


openssl rsa -in ./private/{{ key_name }}.key.pem -check -noout $passphrase_in

exit 0
