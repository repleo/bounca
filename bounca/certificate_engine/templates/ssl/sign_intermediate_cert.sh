#!/bin/bash -e

cd "$(dirname "$0")"

if [ -z "$1" ]
then
    echo "Please, provide number of days the certificate will be valid as first argument"
fi


passphrase_in=""
if [ -e "./passphrase_in.txt" ]
then
    passphrase_in="-passin file:./passphrase_in.txt"
fi

openssl ca -batch -config ../openssl.cnf -extensions v3_intermediate_ca \
	  -days $1 -notext -md sha256 \
      -in ./csr/{{ key_name }}.csr.pem \
      $passphrase_in \
      -out ./certs/{{ key_name }}.cert.pem

chmod 444 ./certs/{{ key_name }}.cert.pem

cat ./certs/{{ key_name }}.cert.pem \
      ../certs/{{ cert.parent.shortname }}-chain.cert.pem > ./certs/{{ key_name }}-chain.cert.pem
chmod 444 ./certs/{{ key_name }}-chain.cert.pem

exit 0
    
