from hashlib import md5
from flask import request

def hash_all(*args):
    strings = map(str, args)
    hashed = md5(':'.join(strings))
    return hashed.hexdigest()

def digest(hA1, hA2, qop, realm):
    auth = request.authorization
    return hash_all(hA1, qop, realm, hA2)
