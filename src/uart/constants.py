MATRICULA = bytes([0, 2, 9, 5, 1, 2])

REQUEST_INT = b'\xa1'
REQUEST_FLOAT = b'\xa2'
REQUEST_STRING = b'\xa3'

SEND_INT = b'\xb1'
SEND_FLOAT = b'\xb2'
SEND_STRING = b'\xb3'

ADDRESS = b'\x01'

REQUEST_CODE = b'\x23'
SEND_CODE = b'\x16'

MODBUS_ERRORS = { # https://docs.aveva.com/bundle/sp-cdp-drivers/page/192126.html
    0x01: 'ILLEGAL FUNCTION',
    0x02: 'ILLEGAL DATA ADDRESS',
    0x03: 'ILLEGAL DATA VALUE',
    0x04: 'ILLEGAL RESPONSE LENGTH',
    0x05: 'ACKNOWLEDGE',
    0x06: 'SLAVE DEVICE BUSY',
    0x07: 'NEGATIVE ACKNOWLEDGE',
    0x08: 'MEMORY PARITY ERROR',
    0x0A: 'GATEWAY PATH UNAVAILABLE',
    0x0B: 'GATEWAY TARGET DEVICE FAILED TO RESPOND'
} 

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
