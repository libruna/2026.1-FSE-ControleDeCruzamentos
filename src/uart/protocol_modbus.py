# Protocolo com MODBUS Modificado

# TODO: Calcular e validar o CRC-16 e implementar tratamento de erros

from .crc16 import calculate_crc

def wrap_modbus(address: bytes, function: bytes, payload: bytes):
    p = address + function + payload
    return p + calculate_crc(p)