import os
import subprocess
import tempfile


def get_certificate_info(crt: str) -> str:
    """
    Get Info of certificates

    Arguments: pem - string with certificate
    Returns:   string
    """
    f = tempfile.NamedTemporaryFile(delete=False)
    path = f.name
    f.write(crt.encode("utf8"))
    f.close()
    cert_txt = subprocess.check_output(["openssl", "x509", "-text", "-noout", "-in", path])
    os.unlink(path)
    return cert_txt.decode("utf8")


def get_certificate_fingerprint(crt: str) -> str:
    """
    Get Fingerprint of certificates

    Arguments: pem - string with certificate
    Returns:   string
    """
    f = tempfile.NamedTemporaryFile(delete=False)
    path = f.name
    f.write(crt.encode("utf8"))
    f.close()
    cert_txt = subprocess.check_output(["openssl", "x509", "-fingerprint", "-sha1", "-noout", "-in", path])
    os.unlink(path)
    fingerprint = cert_txt.decode("utf8")
    return fingerprint.split("=")[1].strip()
