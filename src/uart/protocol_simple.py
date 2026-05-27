# protocolo simplificado

from .parser import *

def make_payload(operation : bytes, *data):
    payload = operation
    for d in data:
        payload += d
    return payload
