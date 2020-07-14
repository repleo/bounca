#!/bin/bash -e 

cd "$(dirname "$0")"
export RANDFILE=.rnd

if [ -z "$1" ]
then
    echo "Please, the key name as first argument"
fi

passphrase_in=""
if [ -e "./passphrase_in.txt" ]
then
    passphrase_in="-passin file:./passphrase_in.txt"
fi


openssl rsa -in ./private/$1.key.pem -check -noout $passphrase_in

exit 0
