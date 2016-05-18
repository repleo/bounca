#!/bin/bash -e 

cd "$(dirname "$0")"


openssl x509 -in ./certs/$1.cert.pem -text -noout



exit 0
