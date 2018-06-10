import random
import string


def generate_path(certificate):
    prefix_path = ""
    if certificate.parent and certificate.pk != certificate.parent.pk:
        prefix_path = generate_path(certificate.parent)
    return prefix_path + "/" + str(certificate.shortname)



def random_string_generator(
        size=300,
        chars=string.ascii_uppercase +
        string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
