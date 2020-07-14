#!/bin/bash -e

cd "$(dirname "$0")"
export RANDFILE=.rnd

if [ -z "$1" ]
then
    echo "Please, provide the prefix filename of the certificate as first argument"
fi


passphrase_in=""
if [ -e "./passphrase_in.txt" ]
then
    passphrase_in="-passin file:./passphrase_in.txt"
fi

mkdir -p ./crl/

openssl ca -config ./openssl.cnf \
	  $passphrase_in \
      -gencrl -out ./crl/$1.crl.pem
   

exit 0
