# protocolo simplificado

from constants import MATRICULA
from uart_connection import ser
from parser import *

# OPERAÇÕES
def request_int() -> bytes:
    packet = bytes([0xA1]) + MATRICULA
    print(f'Pacote enviado: {packet}')
    
    ser.write(packet)

    response = ser.read(4)

    if not validate_response(response, 4):
        ser.close()
        return

    print(f'Pacote recebido: {response} -> {raw_bytes_to_int(response)}')
    
    ser.close()

def request_float() -> bytes:
    packet = bytes([0xA2]) + MATRICULA
    print(f'Pacote enviado: {packet}')
    
    ser.write(packet)

    response = ser.read(4)

    if not validate_response(response, 4):
        ser.close()
        return
    
    print(f'Pacote recebido: {response} -> {raw_bytes_to_float(response)}')
    
    ser.close()

def request_string() -> bytes:
    packet = bytes([0xA3]) + MATRICULA
    print(f'Pacote enviado: {packet}')
    
    ser.write(packet)

    str_size = ser.read(1)
    if not validate_response(str_size, 1):
        ser.close()
        return
    
    print(f'Tamanho da string: {str_size} -> {str_size[0]} caracteres')

    response = ser.read(str_size)
    if not validate_response(response, str_size[0]):
        ser.close()
        return
    
    print(f'Pacote recebido: {response} -> STRING ({str_size[0]}): {raw_bytes_to_string(response)}')

    ser.close()
                                                                                 
def send_int(value: int) -> bytes:
    value_in_bytes = int_to_raw_bytes(value)

    packet = bytes([0xB1]) + value_in_bytes + MATRICULA
    print(f'Pacote enviado: {packet} -> op: {value} * {raw_bytes_to_int(MATRICULA)}')

    ser.write(packet)

    response = ser.read(4)

    if not validate_response(response, 4):
        ser.close()
        return
    
    print(f'Pacote recebido: {response} -> {raw_bytes_to_int(response)}')

    ser.close()

def send_float(value: float) -> bytes:
    value_in_bytes = float_to_raw_bytes(value)

    packet = bytes([0xB2]) + value_in_bytes + MATRICULA
    print(f'Pacote enviado: {packet} -> op: {value} * {raw_bytes_to_int(MATRICULA)}')

    ser.write(packet)

    response = ser.read(4)

    if not validate_response(response, 4):
        ser.close()
        return
    
    print(f'Pacote recebido: {response} -> {raw_bytes_to_float(response)}')

    ser.close()

def send_string(value: str) -> bytes:
    value_in_bytes = string_to_raw_bytes(value)
    size = len(value_in_bytes)

    packet = bytes([0xB3]) + bytes([size]) + value_in_bytes + MATRICULA
    print(f'Pacote enviado: {packet} -> {value} + {raw_bytes_to_int(MATRICULA)}')

    ser.write(packet)

    str_size = ser.read(1)

    if not validate_response(str_size, 1):
        ser.close()
        return
    
    print(f'Tamanho da string: {str_size}')

    response = ser.read(str_size[0])

    if not validate_response(response, str_size[0]):
        ser.close()
        return
    
    print(f'Pacote recebido: {response} -> STRING ({str_size[0]}): {raw_bytes_to_string(response)}')

    ser.close()

def validate_response(response: bytes, expected_size: int) -> bool:
    if len(response) != expected_size:
        print(f'ERRO: timeout exception -> esperava {expected_size} recebeu {len(response)}')
        return False
    return True