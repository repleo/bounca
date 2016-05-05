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

import subprocess 

def generate_root_ca(certificate, passphrase_out):
    openssl_cnf_template_name = 'ssl/openssl-root.cnf'
    generate_key_template_name = 'ssl/generate_key.sh'
    generate_cert_template_name = 'ssl/generate_cert.sh'

    root_path = settings.CA_ROOT + "/" + str(certificate.shortname) + "/"
    logger.info("Create directory for ROOT Certificate " + str(Certificate) + " with the path: " + root_path)
    os.makedirs(root_path,exist_ok=True)
    os.makedirs(root_path + "certs" ,exist_ok=True)
    os.makedirs(root_path + "newcerts" ,exist_ok=True)
    os.makedirs(root_path + "private" ,exist_ok=True)
    os.chmod(root_path + "private", 0o700)
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


    

    logger.info("Files for ROOT CA created")
    
    logger.info("Generate ROOT CA key")

    with open(root_path +'passphrase_out.txt','w') as f:
        f.write(passphrase_out)
    os.chmod(root_path +'passphrase_out.txt', 0o600)
        
    c = {
        'key_name': 'ca',
        'key_length': '4096',
    }
    generate_ca_key_script = loader.render_to_string(generate_key_template_name, c)
    with open(root_path +'generate_ca_key.sh','w') as f:
        f.write(generate_ca_key_script)
    os.chmod(root_path +'generate_ca_key.sh', 0o755)
    
    returncode = subprocess.call([root_path + "generate_ca_key.sh"])
    os.remove(root_path +'passphrase_out.txt')
    if returncode != 0:
        raise Exception("Failed to generate CA key")
    
    
    
    
    
    logger.info("Generate ROOT CA certificate")

    with open(root_path +'passphrase_in.txt','w') as f:
        f.write(passphrase_out)
    os.chmod(root_path +'passphrase_in.txt', 0o600)
    c = {
        'key_name': 'ca',
        'key_length': '4096',
    }
    generate_ca_cert_script = loader.render_to_string(generate_cert_template_name, c)
    with open(root_path +'generate_ca_cert.sh','w') as f:
        f.write(generate_ca_cert_script)
    os.chmod(root_path +'generate_ca_cert.sh', 0o755)
    
    returncode = subprocess.call([root_path + "generate_ca_cert.sh",str(certificate.days_valid),certificate.dn.subj])
    os.remove(root_path +'passphrase_in.txt')
    if returncode != 0:
        raise Exception("Failed to generate CA certificate")
    
    
    return returncode
