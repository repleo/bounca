from OpenSSL import crypto

TYPE_RSA = crypto.TYPE_RSA
TYPE_DSA = crypto.TYPE_DSA


def createCertRequest(pkey, digest="sha256", **name):
    """
    Create a certificate request.

    Arguments: pkey   - The key to associate with the request
               digest - Digestion method to use for signing, default is sha256
               **name - The name of the subject of the request, possible
                        arguments are:
                          C     - Country name
                          ST    - State or province name
                          L     - Locality name
                          O     - Organization name
                          OU    - Organizational unit name
                          CN    - Common name
                          emailAddress - E-mail address
    Returns:   The certificate request in an X509Req object
    """
    req = crypto.X509Req()
    subj = req.get_subject()

    for key, value in name.items():
        setattr(subj, key, value)

    req.set_pubkey(pkey)
    req.sign(pkey, digest)
    return req




# #!/bin/bash -e
#
#
# passphrase_in=""
# if [ -e "./passphrase_in.txt" ]
# then
#     passphrase_in="-passin file:./passphrase_in.txt"
# fi
#
# if ! [ -z "$2" ]
# then
#   openssl req -config ./openssl.cnf \
#       -key ./private/{{ key_name }}.key.pem \
#       -new -x509 -days $1 -sha256 -extensions v3_ca \
#       -subj "$2" \
#       $passphrase_in \
#       -out ./certs/{{ key_name }}.cert.pem
# else
#   openssl req -config ./openssl.cnf \
#       -key ./private/{{ key_name }}.key.pem \
#       -new -x509 -days $1 -sha256 -extensions v3_ca \
#       $passphrase_in \
#       -out ./certs/{{ key_name }}.cert.pem
# fi
#
#
# cat ./certs/{{ key_name}}.cert.pem > ./certs/{{ key_name }}-chain.cert.pem
# chmod 444 ./certs/{{ key_name  }}-chain.cert.pem




