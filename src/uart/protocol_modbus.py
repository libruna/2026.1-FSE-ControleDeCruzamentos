# Protocolo com MODBUS Modificado

# TODO: Calcular e validar o CRC-16 e implementar tratamento de erros

from .constants import *
from .uart_connection import open_serial
from .parser import *
from .crc16 import calculate_crc

# OPERAÇÕES
def request_int() -> bytes:
    ser = open_serial()

    payload = b"".join([
        ADDRESS,
        REQUEST_CODE,
        REQUEST_INT,
        MATRICULA,
    ])
    
    packet = payload + calculate_crc(payload)

    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    response = ser.read(4)
    print(f'Pacote recebido: {response} -> {raw_bytes_to_int(response)}')

    ser.close()

def request_float() -> bytes:
    ser = open_serial()

    payload = b"".join([
        ADDRESS,
        REQUEST_CODE,
        REQUEST_FLOAT,
        MATRICULA
    ])

    packet = payload + calculate_crc(payload)

    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    response = ser.read(4)
    print(f'Pacote recebido: {response} -> {raw_bytes_to_float(response)}')

    ser.close()

def request_string() -> bytes:
    ser = open_serial()

    payload = b"".join([
        ADDRESS,
        REQUEST_CODE, 
        REQUEST_STRING,
        MATRICULA
    ])

    packet = payload + calculate_crc(payload)

    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    str_size = ser.read(1)
    print(f'Tamanho da string: {str_size} -> {str_size[0]} caracteres')

    response = ser.read(str_size)
    print(f'Pacote recebido: {response} -> STRING ({str_size[0]}): {raw_bytes_to_string(response)}')

    ser.close()

def send_int(value: int) -> bytes:
    ser = open_serial()

    value_le = int_to_raw_bytes(value)

    payload = b"".join([
        ADDRESS,
        REQUEST_CODE,
        SEND_INT,
        value_le,
        MATRICULA
    ])

    packet = payload + calculate_crc(payload)
    
    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    response = ser.read(4)
    print(f'Pacote recebido: {response} -> {raw_bytes_to_int(response)}')

    ser.close()

def send_float(value: float) -> bytes:
    ser = open_serial()

    value_le = float_to_raw_bytes(value)

    payload = b"".join([
        ADDRESS,
        REQUEST_CODE,
        SEND_FLOAT,
        value_le,
        MATRICULA
    ])

    packet = payload + calculate_crc(payload)

    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    response = ser.read(4)
    print(f'Pacote recebido: {response} -> {raw_bytes_to_float(response)}')

    ser.close()

def send_string(value: str) -> bytes:
    ser = open_serial()

    value_in_bytes = string_to_raw_bytes(value)
    str_size = len(value_in_bytes)

    payload = b"".join([
        ADDRESS,
        REQUEST_CODE,
        SEND_STRING,
        bytes([str_size]),
        value_in_bytes,
        MATRICULA
    ])

    packet = payload + calculate_crc(payload)

    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    str_size = ser.read(1)
    print(f'Tamanho da string: {str_size}')

    response = ser.read(str_size[0])
    print(f'Pacote recebido: {response} -> STRING ({str_size[0]}): {raw_bytes_to_string(response)}')

    ser.close()