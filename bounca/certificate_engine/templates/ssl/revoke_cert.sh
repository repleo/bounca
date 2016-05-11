#!/bin/bash -e

cd "$(dirname "$0")"

if [ -z "$1" ]
then
    echo "Please, provide the prefix filename of the certificate as first argument"
fi

if [ -z "$2" ]
then
    echo "Please, provide the prefix label of the revoked certificate as second argument"
fi

passphrase_in=""
if [ -e "passphrase_in.txt" ]
then
    passphrase_in="-passin file:passphrase_in.txt"
fi

mkdir -p certs/{{ cert_subdir }}/revoked/
mkdir -p private/{{ cert_subdir }}/revoked/

openssl ca -batch -config openssl.cnf \
	  $passphrase_in \
      -revoke certs/{{ cert_subdir }}/$1.cert.pem
      
mv certs/{{ cert_subdir }}/$1.cert.pem certs/{{ cert_subdir }}/revoked/$2-$1.cert.pem
mv certs/{{ cert_subdir }}/$1-chain.cert.pem certs/{{ cert_subdir }}/revoked/$2-$1-chain.cert.pem
mv private/{{ cert_subdir }}/$1.key.pem private/{{ cert_subdir }}/revoked/$2-$1.key.pem


exit 0
