# protocolo simplificado

from .constants import *
from .uart_connection import open_serial
from .parser import *

# OPERAÇÕES
def request_int() -> bytes:
    ser = open_serial()

    packet = REQUEST_INT + MATRICULA
    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    response = ser.read(4)

    if not validate_response(response, 4):
        ser.close()
        return

    print(f'Pacote recebido: {response} -> {raw_bytes_to_int(response)}')

    ser.close()

def request_float() -> bytes:
    ser = open_serial()

    packet = REQUEST_FLOAT + MATRICULA
    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    response = ser.read(4)

    if not validate_response(response, 4):
        ser.close()
        return

    print(f'Pacote recebido: {response} -> {raw_bytes_to_float(response)}')

    ser.close()

def request_string() -> bytes:
    ser = open_serial()

    packet = REQUEST_STRING + MATRICULA
    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    str_size = ser.read(1)
    if not validate_response(str_size, 1):
        ser.close()
        return

    print(f'Tamanho da string: {str_size} -> {str_size[0]} caracteres')

    response = ser.read(str_size[0])
    if not validate_response(response, int(str_size[0])):
        ser.close()
        return

    print(response)

    print(f'Pacote recebido: {response} -> STRING ({str_size[0]}): {raw_bytes_to_string(response)}')

    ser.close()

def send_int(value: int) -> bytes:
    ser = open_serial()

    value_le = int_to_raw_bytes(value)

    packet = SEND_INT + value_le + MATRICULA
    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    response = ser.read(4)

    if not validate_response(response, 4):
        ser.close()
        return

    print(f'Pacote recebido: {response} -> {raw_bytes_to_int(response)}')

    ser.close()

def send_float(value: float) -> bytes:
    ser = open_serial()

    value_le = float_to_raw_bytes(value)

    packet = SEND_FLOAT + value_le + MATRICULA
    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    response = ser.read(4)

    if not validate_response(response, 4):
        ser.close()
        return

    print(f'Pacote recebido: {response} -> {raw_bytes_to_float(response)}')

    ser.close()

def send_string(value: str) -> bytes:
    ser = open_serial()

    value_in_bytes = string_to_raw_bytes(value)
    size = len(value_in_bytes)

    packet = SEND_STRING + bytes([size]) + value_in_bytes + MATRICULA
    print(f'Pacote enviado: {packet}')

    ser.write(packet)

    str_size = ser.read(1)

    if not validate_response(str_size, 1):
        ser.close()
        return

    print(f'Tamanho da string: {str_size[0]}')

    response = ser.read(str_size[0])

    if not validate_response(response, str_size[0]):
        ser.close()
        return

    print(f'Pacote recebido: {response} -> STRING ({str_size[0]}): {raw_bytes_to_string(response)}')

    ser.close()

def validate_response(response: bytes, expected_size: int) -> bool:
    if len(response) != expected_size: # se entrar no if, ser.read() retornou vazio por timeout
        print(f'ERRO: timeout exception -> esperava {expected_size} recebeu {len(response)}')
        return False
    return True
