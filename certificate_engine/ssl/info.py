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
    return str(cert_txt)
