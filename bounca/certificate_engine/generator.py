'''
Created on 5 mei 2016

@author: Jeroen Arnoldus
'''
from django.conf import settings
import os
from django.template import loader

import logging
from bounca.x509_pki.models import Certificate
logger = logging.getLogger(__name__)


def generate_root_ca(certificate):
    openssl_cnf_template_name = 'ssl/openssl-root.cnf'
    root_path = settings.CA_ROOT + "/" + str(certificate.shortname) + "/"
    logger.info("Create directory for ROOT Certificate " + str(Certificate) + " with the path: " + root_path)
    os.makedirs(root_path,exist_ok=True)
    os.makedirs(root_path + "certs" ,exist_ok=True)
    os.makedirs(root_path + "newcerts" ,exist_ok=True)
    os.makedirs(root_path + "private" ,exist_ok=True)
    os.chmod(root_path + "private", 700)
    open(root_path +'index.txt','w')
    with open(root_path +'serial','w') as f:
        f.write("1000")

    c = {
        'cert': certificate,
        'root_path': root_path,
    }
    openssl_cnf = loader.render_to_string(openssl_cnf_template_name, c)
    with open(root_path +'openssl.cnf','w') as f:
        f.write(openssl_cnf)

    