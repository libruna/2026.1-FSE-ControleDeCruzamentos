# protocolo simplificado

def make_payload(operation : bytes, *data):
    payload = operation
    for d in data:
        payload += d
    return payload
