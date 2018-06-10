import os

from django.conf import settings

from bounca.certificate_engine.utils import generate_path
from bounca.x509_pki.types import CertificateTypes


class generate_key_path(object):

    def __init__(self, f):
        self.f = f

    def __call__(self, certificate, *args):
        key_path = generate_path(certificate.parent) if (certificate.type == CertificateTypes.CLIENT_CERT or certificate.type == CertificateTypes.SERVER_CERT) else generate_path(certificate)
        root_path = settings.CERTIFICATE_REPO_PATH + key_path + "/"
        os.makedirs(root_path, exist_ok=True)
        return self.f(
            certificate,
            *args,
            key_path=key_path,
            root_path=root_path)


class write_passphrase_files(object):

    def __init__(self, f):
        self.f = f

    def __call__(self, certificate, *args, key_path='.', root_path='.'):
        try:
            if certificate.passphrase_out:
                with open(root_path + 'passphrase_out.txt', 'w') as f:
                    f.write(certificate.passphrase_out)
                os.chmod(root_path + 'passphrase_out.txt', 0o600)
            else:
                try:
                    os.remove(root_path + 'passphrase_out.txt')
                except FileNotFoundError:
                    pass

            if certificate.passphrase_in:
                with open(root_path + 'passphrase_in.txt', 'w') as f:
                    f.write(certificate.passphrase_in)
                os.chmod(root_path + 'passphrase_in.txt', 0o600)
            else:
                try:
                    os.remove(root_path + 'passphrase_in.txt')
                except FileNotFoundError:
                    pass

            result = self.f(
                certificate,
                *args,
                key_path=key_path,
                root_path=root_path)

            with open(root_path + 'passphrase_out.txt', 'w') as f:
                f.write(random_string_generator())
            os.remove(root_path + 'passphrase_out.txt')
            with open(root_path + 'passphrase_in.txt', 'w') as f:
                f.write(random_string_generator())
            os.remove(root_path + 'passphrase_in.txt')

            return result
        except Exception as e:
            with open(root_path + 'passphrase_out.txt', 'w') as f:
                f.write(random_string_generator())
            os.remove(root_path + 'passphrase_out.txt')
            with open(root_path + 'passphrase_in.txt', 'w') as f:
                f.write(random_string_generator())
            os.remove(root_path + 'passphrase_in.txt')
            raise e
