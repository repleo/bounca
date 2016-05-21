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
from subprocess import CalledProcessError


def generate_path(certificate):
    prefix_path=""
    if certificate.parent and certificate.pk != certificate.parent.pk:
        prefix_path=generate_path(certificate.parent)
    return prefix_path + "/" + str(certificate.shortname)

class generate_key_path(object):

    def __init__(self, f):
        self.f = f

    def __call__(self,certificate,*args):
        if(certificate.type==CertificateTypes.CLIENT_CERT or certificate.type==CertificateTypes.SERVER_CERT):
            key_path = generate_path(certificate.parent)
        else:
            key_path = generate_path(certificate)
        root_path = settings.CA_ROOT + key_path + "/"
        os.makedirs(root_path,exist_ok=True)
        return self.f(certificate, *args , key_path=key_path, root_path=root_path)
            
            

            
import string
import random
def random_string_generator(size=300, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class write_passphrase_files(object):

    def __init__(self, f):
        self.f = f

    def __call__(self,certificate, *args, key_path='.', root_path='.'):
        try:
            if certificate.passphrase_out:
                with open(root_path +'passphrase_out.txt','w') as f:
                    f.write(certificate.passphrase_out)    
                os.chmod(root_path +'passphrase_out.txt', 0o600)
            else:
                try:
                    os.remove(root_path +'passphrase_out.txt')
                except FileNotFoundError:
                    pass
                
            if certificate.passphrase_in:
                with open(root_path +'passphrase_in.txt','w') as f:
                    f.write(certificate.passphrase_in)
                os.chmod(root_path +'passphrase_in.txt', 0o600)
            else:
                try:
                    os.remove(root_path +'passphrase_in.txt')
                except FileNotFoundError:
                    pass
                      
            
            
            result = self.f(certificate, *args , key_path=key_path, root_path=root_path)
            
            with open(root_path +'passphrase_out.txt','w') as f:
                f.write(random_string_generator())
            os.remove(root_path +'passphrase_out.txt')
            with open(root_path +'passphrase_in.txt','w') as f:
                f.write(random_string_generator()) 
            os.remove(root_path +'passphrase_in.txt')  
            
            return result                           
        except Exception as e:
            with open(root_path +'passphrase_out.txt','w') as f:
                f.write(random_string_generator())
            os.remove(root_path +'passphrase_out.txt')
            with open(root_path +'passphrase_in.txt','w') as f:
                f.write(random_string_generator())
            os.remove(root_path +'passphrase_in.txt')          
            raise e
            
@generate_key_path
def generate_files(certificate,openssl_cnf_template_name, key_path='.', root_path='.'):   

    logger.warning("Create directory for certificate " + str(certificate) + " with the path: " + root_path)
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

@generate_key_path
@write_passphrase_files
def generate_key(certificate,generate_key_template_name, key_path='.', root_path='.'):

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

    return returncode


@generate_key_path
@write_passphrase_files
def generate_cert(certificate,generate_cert_template_name, key_path='.', root_path='.'):
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

    return 0

@generate_key_path
@write_passphrase_files
def generate_csr(certificate,generate_csr_template_name, key_path='.', root_path='.'):
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
    return 0

@generate_key_path
@write_passphrase_files
def sign_cert(certificate,sign_cert_template_name, key_path='.', root_path='.'):
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
    return 0

@generate_key_path
def generate_server_cert_creation_script(certificate,generate_signed_cert_template_name, key_path='.', root_path='.'):

    c = {
        'cert': certificate,
        'extensions': 'server',
        'cert_subdir': 'server_cert',
        'key_length': '2048'
    }
    generate_signed_certificate_script = loader.render_to_string(generate_signed_cert_template_name, c)
    with open(root_path +'generate_signed_server_cert_certificate.sh','w') as f:
        f.write(generate_signed_certificate_script)
    os.chmod(root_path +'generate_signed_server_cert_certificate.sh', 0o755)
    return 0

@generate_key_path
def generate_client_cert_creation_script(certificate,generate_signed_cert_template_name, key_path='.', root_path='.'):

    c = {
        'cert': certificate,
        'extensions': 'client',
        'cert_subdir': 'usr_cert',
        'key_length': '2048'
    }
    generate_signed_certificate_script = loader.render_to_string(generate_signed_cert_template_name, c)
    with open(root_path +'generate_signed_usr_cert_certificate.sh','w') as f:
        f.write(generate_signed_certificate_script)
    os.chmod(root_path +'generate_signed_usr_cert_certificate.sh', 0o755)
    return 0

@generate_key_path
def generate_generic_cert_revoke_script(certificate,generate_cert_revoke_template_name,script_name, key_path='.', root_path='.'):

    c = {
        'cert': certificate,
        'cert_subdir': script_name
    }
    generate_signed_certificate_script = loader.render_to_string(generate_cert_revoke_template_name, c)
    with open(root_path +'revoke_%s_certificate.sh'%(script_name),'w') as f:
        f.write(generate_signed_certificate_script)
    os.chmod(root_path +'revoke_%s_certificate.sh'%(script_name), 0o755)
    return 0

@generate_key_path
def generate_generic_crl_file_script(certificate,generate_crl_file_template_name, key_path='.', root_path='.'):

    c = {
        'cert': certificate
   }
    generate_signed_certificate_script = loader.render_to_string(generate_crl_file_template_name, c)
    with open(root_path +'generate_crl.sh','w') as f:
        f.write(generate_signed_certificate_script)
    os.chmod(root_path +'generate_crl.sh', 0o755)
    return 0

def generate_server_cert_revoke_script(certificate,generate_cert_revoke_template_name):
    return generate_generic_cert_revoke_script(certificate,generate_cert_revoke_template_name,"server")

def generate_client_cert_revoke_script(certificate,generate_cert_revoke_template_name):
    return generate_generic_cert_revoke_script(certificate,generate_cert_revoke_template_name,"client")

@generate_key_path
def generate_certificate_info_script(certificate,generate_certificate_info_template_name, key_path='.', root_path='.'):

    c = {
        'cert': certificate
    }
    generate_certificate_info_certificate_script = loader.render_to_string(generate_certificate_info_template_name, c)
    with open(root_path +'get_certificate_info.sh','w') as f:
        f.write(generate_certificate_info_certificate_script)
    os.chmod(root_path +'get_certificate_info.sh', 0o755)
    return 0

@generate_key_path
def generate_test_passphrase_script(certificate,generate_test_passphrase_template_name, key_path='.', root_path='.'):

    c = {
        'cert': certificate
    }
    generate_test_passphrase_script = loader.render_to_string(generate_test_passphrase_template_name, c)
    with open(root_path +'test_passphrase_key.sh','w') as f:
        f.write(generate_test_passphrase_script)
    os.chmod(root_path +'test_passphrase_key.sh', 0o755)
    return 0

def generate_root_ca(certificate):
    openssl_cnf_template_name = 'ssl/openssl-root.cnf'
    generate_key_template_name = 'ssl/generate_key.sh'
    generate_cert_template_name = 'ssl/generate_cert.sh'
    generate_cert_info_template_name = 'ssl/get_certificate_info.sh'
    generate_test_passphrase_template_name = 'ssl/test_passphrase_key.sh'
    generate_crl_file_template_name ='ssl/generate_crl.sh'

    logger.info("Generate files for ROOT CA")
    generate_files(certificate,openssl_cnf_template_name)

    logger.info("Generate ROOT CA key")
    generate_key(certificate,generate_key_template_name)

    logger.info("Generate ROOT CA certificate")
    generate_cert(certificate,generate_cert_template_name)

    logger.info("Generate get_certificate_info.sh")
    generate_certificate_info_script(certificate,generate_cert_info_template_name)

    logger.info("Generate test_passphrase_key.sh")
    generate_test_passphrase_script(certificate,generate_test_passphrase_template_name)
 
    logger.warning("Create CRL File script")
    generate_generic_crl_file_script(certificate,generate_crl_file_template_name)
      
    logger.info("ROOT CA created")    
    return 0


def generate_intermediate_ca(certificate):
    openssl_cnf_template_name = 'ssl/openssl-intermediate.cnf'
    generate_key_template_name = 'ssl/generate_key.sh'
    generate_csr_template_name = 'ssl/generate_intermediate_csr.sh'
    generate_signcert_template_name = 'ssl/sign_intermediate_cert.sh'
    generate_signed_cert_template_name = 'ssl/generate_signed_cert.sh'
    generate_cert_revoke_template_name = 'ssl/revoke_cert.sh'
    generate_cert_info_template_name = 'ssl/get_certificate_info.sh'
    generate_test_passphrase_template_name = 'ssl/test_passphrase_key.sh'
    generate_crl_file_template_name ='ssl/generate_crl.sh'

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

    logger.warning("Create INTERMEDIATE CA CRL File script")
    generate_generic_crl_file_script(certificate,generate_crl_file_template_name)

    logger.info("Generate get_certificate_info.sh")
    generate_certificate_info_script(certificate,generate_cert_info_template_name)

    logger.info("Generate test_passphrase_key.sh")
    generate_test_passphrase_script(certificate,generate_test_passphrase_template_name)
 
               
    logger.warning("INTERMEDIATE CA created")    
    return returncode

@generate_key_path
@write_passphrase_files
def generate_server_cert(certificate, key_path='.', root_path='.'):
    openssl_cnf_template_name = 'ssl/openssl-server.cnf'

    c = {
        'cert': certificate,
        'key_path': key_path,
        'root_path': root_path,
    }
    openssl_cnf = loader.render_to_string(openssl_cnf_template_name, c)
    with open(root_path +'openssl-server-%s.cnf' % certificate.shortname,'w') as f:
        f.write(openssl_cnf)
        
    logger.warning("Create signed server certificate")
    subprocess.check_output([root_path + "generate_signed_server_certificate.sh",certificate.shortname,str(certificate.days_valid),certificate.dn.subj,' '.join(certificate.dn.subjectAltNames)])
    
    try:
        os.remove(root_path + 'openssl-server-%s.cnf' % certificate.shortname)
    except FileNotFoundError:
        pass
    return 0

@generate_key_path
@write_passphrase_files
def generate_client_cert(certificate, key_path='.', root_path='.'):
    openssl_cnf_template_name = 'ssl/openssl-client.cnf'

    c = {
        'cert': certificate,
        'key_path': key_path,
        'root_path': root_path,
    }
    openssl_cnf = loader.render_to_string(openssl_cnf_template_name, c)
    with open(root_path +'openssl-client-%s.cnf' % certificate.shortname,'w') as f:
        f.write(openssl_cnf)
            
    logger.warning("Create signed client certificate")
    subprocess.check_output([root_path + "generate_signed_client_certificate.sh",certificate.shortname,str(certificate.days_valid),certificate.dn.subj,' '.join(certificate.dn.subjectAltNames)])
    try:
        os.remove(root_path + 'openssl-client-%s.cnf' % certificate.shortname)
    except FileNotFoundError:
        pass
    return 0

@generate_key_path
@write_passphrase_files
def revoke_server_cert(certificate, key_path='.', root_path='.'):
    logger.warning("Revoke server certificate")
    subprocess.check_output([root_path + "revoke_server_certificate.sh",certificate.shortname,str(certificate.slug_revoked_at)])
    return 0

@generate_key_path
@write_passphrase_files
def revoke_client_cert(certificate, key_path='.', root_path='.'):
    logger.warning("Revoke client certificate")
    subprocess.check_output([root_path + "revoke_client_certificate.sh",certificate.shortname,str(certificate.slug_revoked_at)])
    return 0

@generate_key_path
def get_certificate_info(certificate, key_path='.', root_path='.'):
    logger.warning("Get certificate info")
    path=certificate.shortname
    if(certificate.type==CertificateTypes.CLIENT_CERT):
        path="client/" + certificate.shortname
    if(certificate.type==CertificateTypes.SERVER_CERT):
        path="server/" + certificate.shortname
    out = subprocess.check_output([root_path + "get_certificate_info.sh",path])
    return out

@generate_key_path
@write_passphrase_files
def is_passphrase_in_valid(certificate, key_path='.', root_path='.'):
    logger.warning("Test passphrase in of certificate")
    path=certificate.shortname
    if(certificate.type==CertificateTypes.CLIENT_CERT):
        path="client/" + certificate.shortname
    if(certificate.type==CertificateTypes.SERVER_CERT):
        path="server/" + certificate.shortname
    try:
        subprocess.check_output([root_path + "test_passphrase_key.sh",path])
        return True
    except CalledProcessError:
        return False
    
@generate_key_path
@write_passphrase_files
def generate_crl_file(certificate, key_path='.', root_path='.'):
    logger.warning("Generate CRL File")
    subprocess.check_output([root_path + "generate_crl.sh",certificate.shortname])
    return 0


