import random
import string


def new_token(length=44):
    r = random.SystemRandom()
    return "".join(r.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(length))
