#!/bin/bash -e 

cd "$(dirname "$0")"
export RANDFILE=.rnd

openssl x509 -in ./certs/$1.cert.pem -text -noout



exit 0
