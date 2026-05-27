MATRICULA = bytes([6, 5, 4, 3, 2, 2])

REQUEST_INT = b'\xa1'
REQUEST_FLOAT = b'\xa2'
REQUEST_STRING = b'\xa3'

SEND_INT = b'\xb1'
SEND_FLOAT = b'\xb2'
SEND_STRING = b'\xb3'

ADDRESS = b'\x01'

REQUEST_CODE = b'\x23'
SEND_CODE = b'\x16'

def const_nome(c):
    if c == REQUEST_INT:
        return 'Solicita inteiro'
    elif c == REQUEST_FLOAT:
        return 'Solicita float'
    elif c == REQUEST_STRING:
        return 'Solicita string'
    elif c == SEND_INT:
        return 'Envia inteiro'
    elif c == SEND_FLOAT:
        return 'Envia float'
    elif c == SEND_STRING:
        return 'Envia string'
