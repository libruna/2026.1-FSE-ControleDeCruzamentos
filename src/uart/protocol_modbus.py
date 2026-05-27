# Protocolo com MODBUS Modificado

from .crc16 import calculate_crc

def wrap_modbus(address: bytes, function: bytes, payload: bytes):
    p = address + function + payload
    return p + calculate_crc(p)