#!/bin/bash -e

cd "$(dirname "$0")"

if [ -z "$1" ]
then
    echo "Please, provide the prefix filename of the certificate as first argument"
fi


if [ -z "$2" ]
then
    echo "Please, provide number of days the certificate will be valid as second argument"
fi

mkdir -p ./private/{{ cert_subdir }}/
openssl genrsa -out ./private/{{ cert_subdir }}/$1.key.pem {{ key_length }}
chmod 400 ./private/{{ cert_subdir }}/$1.key.pem


passphrase_in=""
if [ -e "passphrase_in.txt" ]
then
    passphrase_in="-passin file:./passphrase_in.txt"
fi

passphrase_out=""
if [ -e "./passphrase_out.txt" ]
then
    passphrase_out="-passout file:./passphrase_out.txt"
fi

opensslcnf="./openssl.cnf"
if [ -e "./openssl-{{ cert_subdir }}-$1.cnf" ]
then
    opensslcnf="./openssl-{{ cert_subdir }}-$1.cnf"
fi




mkdir -p ./csr/{{ cert_subdir }}/
if ! [ -z "$3" ]
then
  openssl req -config $opensslcnf -new -sha256\
      -key ./private/{{ cert_subdir }}/$1.key.pem \
      -subj "$3" \
      $passphrase_in \
      $passphrase_out \
      -out ./csr/{{ cert_subdir }}/$1.csr.pem
else
  openssl req -config $opensslcnf -new -sha256\
      -key ./private/{{ cert_subdir }}/$1.key.pem \
      $passphrase_in \
      $passphrase_out \
      -out ./csr/{{ cert_subdir }}/$1.csr.pem
fi

mkdir -p ./certs/{{ cert_subdir }}/
openssl ca -batch -config $opensslcnf -extensions {{ extensions }} \
	  -days $2 -notext -md sha256 \
      -in ./csr/{{ cert_subdir }}/$1.csr.pem \
      $passphrase_in \
      -out ./certs/{{ cert_subdir }}/$1.cert.pem
      
chmod 444 ./certs/{{ cert_subdir }}/$1.cert.pem
      
cat ./certs/{{ cert_subdir }}/$1.cert.pem \
    ./certs/{{ cert.shortname }}-chain.cert.pem > ./certs/{{ cert_subdir }}/$1-chain.cert.pem
chmod 444 ./certs/{{ cert_subdir }}/$1-chain.cert.pem

passphrase_p12_out="-passout pass:"
passphrase_p12_in=""
if [ -e "./passphrase_out.txt" ]
then
    passphrase_p12_out="-passout file:./passphrase_out.txt"
    passphrase_p12_in="-passin file:./passphrase_out.txt"
fi

openssl pkcs12 -export \
  $passphrase_p12_in\
  $passphrase_p12_out\
  -out ./private/{{ cert_subdir }}/$1.p12 \
  -inkey ./private/{{ cert_subdir }}/$1.key.pem \
  -in ./certs/{{ cert_subdir }}/$1.cert.pem \
  -certfile ./certs/{{ cert.shortname }}-chain.cert.pem

exit 0
