'''
Created on 5 mei 2016

@author: Jeroen Arnoldus
'''
from django.conf import settings
import os
from django.template import loader

from bounca.x509_pki.models import CertificateTypes

import logging
logger = logging.getLogger(__name__)

import subprocess 

def generate_path(certificate):
    prefix_path=""
    if certificate.parent and certificate.pk != certificate.parent.pk:
        prefix_path=generate_path(certificate.parent)
    return prefix_path + "/" + str(certificate.shortname)

def generate_files(certificate,openssl_cnf_template_name):
    key_path = generate_path(certificate)
    root_path = settings.CA_ROOT + key_path + "/"
    

    logger.warning("Create directory for certificate " + str(certificate) + " with the path: " + root_path)
    os.makedirs(root_path,exist_ok=True)
    os.makedirs(root_path + "certs" ,exist_ok=True)
    if certificate.type == CertificateTypes.INTERMEDIATE:
        os.makedirs(root_path + "crl" ,exist_ok=True)
        os.makedirs(root_path + "csr" ,exist_ok=True)
        with open(root_path +'crlnumber','w') as f:
            f.write("1000")

    os.makedirs(root_path + "newcerts" ,exist_ok=True)
    os.makedirs(root_path + "private" ,exist_ok=True)
    os.chmod(root_path + "private", 0o700)
    open(root_path +'index.txt','w')
    with open(root_path +'index.txt.attr','w') as f:
        f.write("unique_subject = yes")

    with open(root_path +'serial','w') as f:
        f.write("1000")

    c = {
        'cert': certificate,
        'key_path': key_path,
        'root_path': root_path,
    }
    openssl_cnf = loader.render_to_string(openssl_cnf_template_name, c)
    with open(root_path +'openssl.cnf','w') as f:
        f.write(openssl_cnf)
        
    return 0


def generate_key(certificate,generate_key_template_name):
    key_path = generate_path(certificate)
    root_path = settings.CA_ROOT + key_path + "/"

    with open(root_path +'passphrase_out.txt','w') as f:
        f.write(certificate.passphrase_out)
    os.chmod(root_path +'passphrase_out.txt', 0o600)
    
    key_name=certificate.shortname
        
    c = {
        'key_name': key_name,
        'key_root_path': key_path,
        'key_length': '4096',
    }
    generate_ca_key_script = loader.render_to_string(generate_key_template_name, c)
    with open(root_path +'generate_%s_key.sh' %(key_name),'w') as f:
        f.write(generate_ca_key_script)
    os.chmod(root_path +'generate_%s_key.sh' %(key_name), 0o755)
    
    returncode = subprocess.check_output([root_path + 'generate_%s_key.sh' %(key_name)])
    os.remove(root_path +'passphrase_out.txt')
    return returncode



def generate_cert(certificate,generate_cert_template_name):
    key_path = generate_path(certificate)
    root_path = settings.CA_ROOT + key_path + "/"
    with open(root_path +'passphrase_in.txt','w') as f:
        f.write(certificate.passphrase_out)
    os.chmod(root_path +'passphrase_in.txt', 0o600)
           
    key_name=certificate.shortname

    c = {
        'key_name':key_name,
        'key_root_path': key_path,
        'key_length': '4096',
    }
    generate_ca_cert_script = loader.render_to_string(generate_cert_template_name, c)
    with open(root_path +'generate_%s_cert.sh'%(key_name),'w') as f:
        f.write(generate_ca_cert_script)
    os.chmod(root_path +'generate_%s_cert.sh'%(key_name), 0o755)
    
    subprocess.check_output([root_path + "generate_%s_cert.sh"%(key_name),str(certificate.days_valid),certificate.dn.subj])
    os.remove(root_path +'passphrase_in.txt')
    return 0


def generate_csr(certificate,generate_csr_template_name):
    key_path = generate_path(certificate)
    root_path = settings.CA_ROOT + key_path + "/"
    with open(root_path +'passphrase_in.txt','w') as f:
        f.write(certificate.passphrase_out)
    os.chmod(root_path +'passphrase_in.txt', 0o600)
    
    key_name=certificate.shortname

    c = {
        'key_name': key_name,
        'key_root_path': key_path,
        'key_length': '4096',
    }
    generate_csr_script = loader.render_to_string(generate_csr_template_name, c)
    with open(root_path +'generate_csr.sh','w') as f:
        f.write(generate_csr_script)
    os.chmod(root_path +'generate_csr.sh', 0o755)
    
    subprocess.check_output([root_path + "generate_csr.sh",certificate.dn.subj])
    os.remove(root_path +'passphrase_in.txt')
    return 0

def sign_cert(certificate,sign_cert_template_name):
    key_path = generate_path(certificate)
    root_path = settings.CA_ROOT + key_path + "/"
    with open(root_path +'passphrase_in.txt','w') as f:
        f.write(certificate.passphrase_in)
    os.chmod(root_path +'passphrase_in.txt', 0o600)
    
    key_name=certificate.shortname

    c = {
        'key_name': key_name,
        'cert': certificate,
        'key_root_path': key_path,
        'key_length': '4096',
    }
    sign_certificate_script = loader.render_to_string(sign_cert_template_name, c)
    with open(root_path +'sign_certificate.sh','w') as f:
        f.write(sign_certificate_script)
    os.chmod(root_path +'sign_certificate.sh', 0o755)
    
    subprocess.check_output([root_path + "sign_certificate.sh",str(certificate.days_valid)])
    os.remove(root_path +'passphrase_in.txt')
    return 0

def generate_generic_cert_creation_script(certificate,generate_signed_cert_template_name,extensions,script_name):
    key_path = generate_path(certificate)
    root_path = settings.CA_ROOT + key_path + "/"

    c = {
        'cert': certificate,
        'extensions': extensions,
        'cert_subdir': script_name,
        'key_length': '2048'
    }
    generate_signed_certificate_script = loader.render_to_string(generate_signed_cert_template_name, c)
    with open(root_path +'generate_signed_%s_certificate.sh'%(script_name),'w') as f:
        f.write(generate_signed_certificate_script)
    os.chmod(root_path +'generate_signed_%s_certificate.sh'%(script_name), 0o755)
    return 0

def generate_server_cert_creation_script(certificate,generate_signed_cert_template_name):
    return generate_generic_cert_creation_script(certificate,generate_signed_cert_template_name,"server_cert","server")

def generate_client_cert_creation_script(certificate,generate_signed_cert_template_name):
    return generate_generic_cert_creation_script(certificate,generate_signed_cert_template_name,"usr_cert","client")


def generate_generic_cert_revoke_script(certificate,generate_cert_revoke_template_name,script_name):
    key_path = generate_path(certificate)
    root_path = settings.CA_ROOT + key_path + "/"

    c = {
        'cert': certificate,
        'cert_subdir': script_name
    }
    generate_signed_certificate_script = loader.render_to_string(generate_cert_revoke_template_name, c)
    with open(root_path +'revoke_%s_certificate.sh'%(script_name),'w') as f:
        f.write(generate_signed_certificate_script)
    os.chmod(root_path +'revoke_%s_certificate.sh'%(script_name), 0o755)
    return 0

def generate_server_cert_revoke_script(certificate,generate_cert_revoke_template_name):
    return generate_generic_cert_revoke_script(certificate,generate_cert_revoke_template_name,"server")

def generate_client_cert_revoke_script(certificate,generate_cert_revoke_template_name):
    return generate_generic_cert_revoke_script(certificate,generate_cert_revoke_template_name,"client")


def generate_root_ca(certificate):
    openssl_cnf_template_name = 'ssl/openssl-root.cnf'
    generate_key_template_name = 'ssl/generate_key.sh'
    generate_cert_template_name = 'ssl/generate_cert.sh'

    logger.info("Generate files for ROOT CA")
    generate_files(certificate,openssl_cnf_template_name)

    logger.info("Generate ROOT CA key")
    generate_key(certificate,generate_key_template_name)

    logger.info("Generate ROOT CA certificate")
    generate_cert(certificate,generate_cert_template_name)
 
    logger.info("ROOT CA created")    
    return 0


def generate_intermediate_ca(certificate):
    openssl_cnf_template_name = 'ssl/openssl-intermediate.cnf'
    generate_key_template_name = 'ssl/generate_key.sh'
    generate_csr_template_name = 'ssl/generate_intermediate_csr.sh'
    generate_signcert_template_name = 'ssl/sign_intermediate_cert.sh'
    generate_signed_cert_template_name = 'ssl/generate_signed_cert.sh'
    generate_cert_revoke_template_name = 'ssl/revoke_cert.sh'


    logger.warning("Generate files for INTERMEDIATE CA")
    returncode = generate_files(certificate,openssl_cnf_template_name)
    if returncode != 0:
        raise Exception("Failed to generate files")
    
    logger.warning("Generate INTERMEDIATE CA key")
    generate_key(certificate,generate_key_template_name)
 
    
    logger.warning("Generate INTERMEDIATE CA signing request")
    generate_csr(certificate,generate_csr_template_name)

    logger.warning("SIGN INTERMEDIATE CA signing request")
    sign_cert(certificate,generate_signcert_template_name)

    logger.warning("Create INTERMEDIATE CA server cert creation script")
    generate_server_cert_creation_script(certificate,generate_signed_cert_template_name)
     
    logger.warning("Create INTERMEDIATE CA client cert creation script")
    generate_client_cert_creation_script(certificate,generate_signed_cert_template_name)

    logger.warning("Create INTERMEDIATE CA server cert revoke script")
    generate_server_cert_revoke_script(certificate,generate_cert_revoke_template_name)
     
    logger.warning("Create INTERMEDIATE CA client cert revoke script")
    generate_client_cert_revoke_script(certificate,generate_cert_revoke_template_name)
               
    logger.warning("INTERMEDIATE CA created")    
    return returncode

def generate_server_cert(certificate):
    key_path = generate_path(certificate.parent)
    root_path = settings.CA_ROOT + key_path + "/"
    with open(root_path +'passphrase_in.txt','w') as f:
        f.write(certificate.passphrase_in)
    os.chmod(root_path +'passphrase_in.txt', 0o600)
    
    if certificate.passphrase_out:
        with open(root_path +'passphrase_out.txt','w') as f:
            f.write(certificate.passphrase_in)
        os.chmod(root_path +'passphrase_out.txt', 0o600)
                
    logger.warning("Create signed server certificate")

    subprocess.check_output([root_path + "generate_signed_server_certificate.sh",certificate.dn.slug_commonName,str(certificate.days_valid),certificate.dn.subj])
    os.remove(root_path +'passphrase_in.txt')
    if certificate.passphrase_out:
        os.remove(root_path +'passphrase_out.txt')
    return 0

def generate_client_cert(certificate):
    key_path = generate_path(certificate.parent)
    root_path = settings.CA_ROOT + key_path + "/"
    with open(root_path +'passphrase_in.txt','w') as f:
        f.write(certificate.passphrase_in)
    os.chmod(root_path +'passphrase_in.txt', 0o600)
    
    if certificate.passphrase_out:
        with open(root_path +'passphrase_out.txt','w') as f:
            f.write(certificate.passphrase_in)
        os.chmod(root_path +'passphrase_out.txt', 0o600)        

    logger.warning("Create signed client certificate")

    subprocess.check_output([root_path + "generate_signed_client_certificate.sh",certificate.dn.slug_commonName,str(certificate.days_valid),certificate.dn.subj])
    os.remove(root_path +'passphrase_in.txt')
    if certificate.passphrase_out:
        os.remove(root_path +'passphrase_out.txt')
    return 0

def revoke_server_cert(certificate):
    key_path = generate_path(certificate.parent)
    root_path = settings.CA_ROOT + key_path + "/"
    with open(root_path +'passphrase_in.txt','w') as f:
        f.write(certificate.passphrase_in)
    os.chmod(root_path +'passphrase_in.txt', 0o600)
                
    logger.warning("Revoke server certificate")

    subprocess.check_output([root_path + "revoke_server_certificate.sh",certificate.dn.slug_commonName,str(certificate.slug_revoked_at)])
    os.remove(root_path +'passphrase_in.txt')
    return 0

def revoke_client_cert(certificate):
    key_path = generate_path(certificate.parent)
    root_path = settings.CA_ROOT + key_path + "/"
    with open(root_path +'passphrase_in.txt','w') as f:
        f.write(certificate.passphrase_in)
    os.chmod(root_path +'passphrase_in.txt', 0o600)
                
    logger.warning("Revoke client certificate")

    subprocess.check_output([root_path + "revoke_client_certificate.sh",certificate.dn.slug_commonName,str(certificate.slug_revoked_at)])
    os.remove(root_path +'passphrase_in.txt')
    return 0



