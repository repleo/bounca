#!/usr/bin/env bash  

cd "$(dirname "$0")"

if [ -z "$1" ]
then
    echo "Please, provide number of days the certificate will be valid as first argument"
fi


passphrase_in=""
if [ -e "passphrase_in.txt" ]
then
    passphrase_in="-passin file:passphrase_in.txt"
fi

if ! [ -z "$2" ]
then
  openssl req -config openssl.cnf \
      -key private/ca.key.pem \
      -new -x509 -days $1 -sha256 -extensions v3_ca \
      -subj "$2" \
      $passphrase_in \
      -out certs/{{ key_name }}.cert.pem
else
  openssl req -config openssl.cnf \
      -key private/ca.key.pem \
      -new -x509 -days $1 -sha256 -extensions v3_ca \
      $passphrase_in \
      -out certs/{{ key_name }}.cert.pem
fi

exit 0
