#!/bin/bash -e

cd "$(dirname "$0")"

passphrase_in=""
if [ -e "./passphrase_out.txt" ]
then
    passphrase_in="-passin file:./passphrase_out.txt"
fi

if ! [ -z "$1" ]
then
  openssl req -config ./openssl.cnf -new -sha256\
      -key ./private/{{ key_name }}.key.pem \
      -subj "$1" \
      $passphrase_in \
      -out ./csr/{{ key_name }}.csr.pem
else
  openssl req -config openssl.cnf -new -sha256\
      -key ./private/{{ key_name }}.key.pem \
      $passphrase_in \
      -out ./csr/{{ key_name }}.csr.pem
fi


exit 0
