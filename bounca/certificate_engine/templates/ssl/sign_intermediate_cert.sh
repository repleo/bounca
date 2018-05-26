#!/bin/bash -e

cd "$(dirname "$0")"
export RANDFILE=.rnd

if [ -z "$1" ]
then
    echo "Please, provide number of days the certificate will be valid as first argument"
fi

#Step into root CA dir
cd ..

passphrase_in=""
if [ -e "./{{ cert.shortname }}/passphrase_in.txt" ]
then
    passphrase_in="-passin file:./{{ cert.shortname }}/passphrase_in.txt"
fi


openssl ca -batch -config ./openssl.cnf -extensions v3_intermediate_ca \
	  -days $1 -notext -md sha256 \
      -in ./{{ cert.shortname }}/csr/{{ key_name }}.csr.pem \
      $passphrase_in \
      -out ./{{ cert.shortname }}/certs/{{ key_name }}.cert.pem

cd {{ cert.shortname }}


chmod 444 ./certs/{{ key_name }}.cert.pem

cat ./certs/{{ key_name }}.cert.pem \
      ../certs/{{ cert.parent.shortname }}-chain.cert.pem > ./certs/{{ key_name }}-chain.cert.pem
chmod 444 ./certs/{{ key_name }}-chain.cert.pem

exit 0
    
