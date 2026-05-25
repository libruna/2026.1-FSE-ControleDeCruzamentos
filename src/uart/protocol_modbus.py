# Protocolo com MODBUS Modificado

# TODO: Calcular e validar o CRC-16 e implementar tratamento de erros

from constants import *
from uart_connection import ser
from parser import *

# OPERAÇÕES
def request_int() -> bytes:
    packet = ADDRESS + REQUEST_CODE + REQUEST_INT + MATRICULA
    print(f'Pacote enviado: {packet}')
    
    ser.write(packet)

    response = ser.read(4)
    print(f'Pacote recebido: {response} -> {raw_bytes_to_int(response)}')
    
    ser.close()

def request_float() -> bytes:
    packet = ADDRESS + REQUEST_CODE + REQUEST_FLOAT + MATRICULA
    print(f'Pacote enviado: {packet}')
    
    ser.write(packet)

    response = ser.read(4)
    print(f'Pacote recebido: {response} -> {raw_bytes_to_float(response)}')
    
    ser.close()

def request_string() -> bytes:
    packet = ADDRESS + REQUEST_CODE + REQUEST_STRING + MATRICULA
    print(f'Pacote enviado: {packet}')
    
    ser.write(packet)

    str_size = ser.read(1)
    print(f'Tamanho da string: {str_size} -> {str_size[0]} caracteres')

    response = ser.read(str_size)
    print(f'Pacote recebido: {response} -> STRING ({str_size[0]}): {raw_bytes_to_string(response)}')

    ser.close()

def send_int(value: int) -> bytes:
    value_le = int_to_raw_bytes(value)

    packet = ADDRESS + REQUEST_CODE + SEND_INT + value_le + MATRICULA + int_to_raw_bytes(value)
    print(f'Pacote enviado: {packet}')
    
    ser.write(packet)

    response = ser.read(4)
    print(f'Pacote recebido: {response} -> {raw_bytes_to_int(response)}')

    ser.close()

def send_float(value: float) -> bytes:
    value_le = float_to_raw_bytes(value)

    packet = ADDRESS + REQUEST_CODE + SEND_FLOAT + value_le + MATRICULA + float_to_raw_bytes(value)
    print(f'Pacote enviado: {packet}')
    
    ser.write(packet)

    response = ser.read(4)
    print(f'Pacote recebido: {response} -> {raw_bytes_to_float(response)}')

    ser.close()

def send_string(value: str) -> bytes:
    value_in_bytes = string_to_raw_bytes(value)
    str_size = len(value_in_bytes)

    packet = ADDRESS + REQUEST_CODE + SEND_STRING + bytes([str_size]) + value_in_bytes + MATRICULA + bytes([str_size]) + value_in_bytes
    print(f'Pacote enviado: {packet}')
    
    ser.write(packet)

    str_size = ser.read(1)
    print(f'Tamanho da string: {str_size}')

    response = ser.read(str_size[0])
    print(f'Pacote recebido: {response} -> STRING ({str_size[0]}): {raw_bytes_to_string(response)}')

    ser.close()