from uart import protocol_simple, protocol_modbus
from uart.constants import *
from uart.parser import *
from uart.uart_connection import connect
import re

VAR_LENGHT = 0

def menu_uart():
    while True:
        print("\n------- UART -------")
        print("1 - Protocolo Simplificado")
        print("2 - Protocolo MODBUS")
        print("0 - Sair")

        option = input("Escolha: ")

        if option == "1":
            menu_simple_protocol()

        elif option == "2":
            menu_modbus_protocol()

        elif option == "0":
            print('Encerrando...')
            break

        else:
            print("Opção inválida")

def menu_simple_protocol():
    while True:
        print('\n------- Protocolo Simplificado -------')
        print('1 - Solicitar inteiro')
        print('2 - Solicitar float')
        print('3 - Solicitar string')
        print('4 - Enviar inteiro')
        print('5 - Enviar float')
        print('6 - Enviar string')
        print('0 - Sair')

        option = input('\nEscolha: ')

        operation = b''
        value = b''

        if option == '1':
            operation = REQUEST_INT

            response = _send_protocol_simple(operation)

            _interpret(operation, response)

        elif option == '2':
            operation = REQUEST_FLOAT

            response = _send_protocol_simple(operation)

            _interpret(operation, response)

        elif option == '3':
            operation = REQUEST_STRING

            response = _send_protocol_simple(operation)

            _interpret(operation, response)

        elif option == '4':
            operation = SEND_INT
            value = int_to_bytes(int(input('Digite um inteiro: ')))

            response = _send_protocol_simple(operation, value)

            _interpret(operation, response)

        elif option == '5':
            operation = SEND_FLOAT
            value = float_to_bytes(float(input('Digite um float: ')))

            response = _send_protocol_simple(operation, value)

            _interpret(operation, response)

        elif option == '6':
            operation = SEND_STRING
            value = string_to_bytes(input('Digite uma string: '))

            response = _send_protocol_simple(operation, value)

            _interpret(operation, response)

        elif option == '0':
            print('Encerrando...')
            break

        else:
            print('Opção inválida')

def menu_modbus_protocol():
    while True:
        print('\n------- Protocolo MODBUS -------')
        print('1 - Solicitar inteiro')
        print('2 - Solicitar float')
        print('3 - Solicitar string')
        print('4 - Enviar inteiro')
        print('5 - Enviar float')
        print('6 - Enviar string')
        print('0 - Sair')

        option = input('\nEscolha: ')

        function = b''
        operation = b''
        value = b''

        if option == '1':
            function = REQUEST_CODE
            operation = REQUEST_INT

            response = _send_protocol_modbus(operation, function)

            _interpret(operation, response, True)

        elif option == '2':
            function = REQUEST_CODE
            operation = REQUEST_FLOAT

            response = _send_protocol_modbus(operation, function)

            _interpret(operation, response, True)

        elif option == '3':
            function = REQUEST_CODE
            operation = REQUEST_STRING

            response = _send_protocol_modbus(operation, function)

            _interpret(operation, response, True)

        elif option == '4':
            function = SEND_CODE
            operation = SEND_INT

            value = int_to_bytes(int(input('Digite um inteiro: ')))

            response = _send_protocol_modbus(operation, function, value)

            _interpret(operation, response, True)

        elif option == '5':
            function = SEND_CODE
            operation = SEND_FLOAT

            value = float_to_bytes(float(input('Digite um float: ')))

            response = _send_protocol_modbus(operation, function, value)

            _interpret(operation, response, True)

        elif option == '6':
            function = SEND_CODE
            operation = SEND_STRING

            value = string_to_bytes(input('Digite uma string: '))

            response = _send_protocol_modbus(operation, function, value)

            _interpret(operation, response, True)

        elif option == '0':
            print('Encerrando...')
            break

        else:
            print('Opção inválida')

def _send_protocol_simple(operation, value = b'') -> bytes:
    payload = protocol_simple.make_payload(operation, len(value).to_bytes(1) if operation == SEND_STRING else b'', value, MATRICULA)

    if operation in (REQUEST_FLOAT, REQUEST_INT, REQUEST_STRING):
        print(f'Pacote enviado: {_strhex(payload)}')
        print(f'                    ^   ^------matrícula-----^')
        print(f'                    op                        \n')
        print(f'op = {const_nome(operation)}')
        print(f'matricula = {raw_bytes_to_int(MATRICULA)}')

    elif operation in (SEND_INT, SEND_FLOAT):
        print(f'Pacote enviado: {_strhex(payload)}')
        print(f'                    ^   ^---valor----^  ^------matrícula-----^')
        print(f'                    op                                        \n')
        print(f'op = {const_nome(operation)}')
        print(f'valor = {bytes_to_float(value) if operation == SEND_FLOAT else bytes_to_int(value)}')
        print(f'matricula = {raw_bytes_to_int(MATRICULA)}')

    else:
        print(f'Pacote enviado: {_strhex(payload)}')
        if(len(value) == 1):
            print(f'                    ^   ^   ^   ^------matrícula-----^')
        if(len(value) == 2):
            print(f'                    ^   ^   ^str-^  ^------matrícula-----^')
        else:
            print(f'                    ^   ^   ^--{'str':-^{(len(value)-2)*4}}--^  ^------matrícula-----^')
        print(f'                    op len {'str' if len(value) == 1 else '  '}                                                      \n')
        print(f'op = {const_nome(operation)}')
        print(f'len (tamanho) = {len(value)}')
        print(f'str = {bytes_to_string(value)}')
        print(f'matricula = {raw_bytes_to_int(MATRICULA)}')

    print()

    response_lenght = VAR_LENGHT if operation in (SEND_STRING, REQUEST_STRING) else 4

    return connect(payload, response_lenght, 5)



def _send_protocol_modbus(operation, function, value = b'') -> bytes:
    payload = protocol_simple.make_payload(operation, len(value).to_bytes(1) if operation == SEND_STRING else b'', value, MATRICULA)

    payload = protocol_modbus.wrap_modbus(ADDRESS, function, payload)

    if operation in (REQUEST_FLOAT, REQUEST_INT, REQUEST_STRING):
        print(f'Pacote enviado: {_strhex(payload)}')
        print(f'                    ^   ^   ^   ^------matrícula-----^  ^CRC-^')
        print(f'                   add fun  op                                \n')
        print(f'add (endereço) = {_strhex(ADDRESS)}')
        print(f'fun (função) = {_strhex(function)}')
        print(f'op = {const_nome(operation)}')
        print(f'matricula = {raw_bytes_to_int(MATRICULA)}')
        print(f'crc = {_strhex(payload[-2:])}')

    elif operation in (SEND_INT, SEND_FLOAT):
        print(f'Pacote enviado: {_strhex(payload)}')
        print(f'                    ^   ^   ^   ^---valor----^  ^------matrícula-----^  ^CRC-^')
        print(f'                   add fun  op                                \n')
        print(f'add (endereço) = {_strhex(ADDRESS)}')
        print(f'fun (função) = {_strhex(function)}')
        print(f'op = {const_nome(operation)}')
        print(f'valor = {bytes_to_float(value) if operation == SEND_FLOAT else bytes_to_int(value)}')
        print(f'matricula = {raw_bytes_to_int(MATRICULA)}')
        print(f'crc = {_strhex(payload[-2:])}')

    else:
        print(f'Pacote enviado: {_strhex(payload)}')
        if(len(value) == 1):
            print(f'                    ^   ^   ^   ^   ^   ^------matrícula-----  ^CRC-^^')
        if(len(value) == 2):
            print(f'                    ^   ^   ^   ^   ^str-^  ^------matrícula-----^  ^CRC-^')
        else:
            print(f'                    ^   ^   ^   ^   ^--{'str':-^{(len(value)-2)*4}}--^  ^------matrícula-----^  ^CRC-^')
        print(f'                   add fun  op len {'str' if len(value) == 1 else '  '}                                                      \n')
        print(f'add (endereço) = {_strhex(ADDRESS)}')
        print(f'fun (função) = {_strhex(function)}')
        print(f'op = {const_nome(operation)}')
        print(f'len (tamanho) = {len(value)}')
        print(f'str = {bytes_to_string(value)}')
        print(f'matricula = {raw_bytes_to_int(MATRICULA)}')
        print(f'crc = {_strhex(payload[-2:])}')

    print()

    response_lenght = VAR_LENGHT if operation in (SEND_STRING, REQUEST_STRING) else 4

    return connect(payload, response_lenght, 5, modbus=True)

def _interpret(operation : bytes, response: bytes, modbus=False):
    print(f'Pacote recebido: {_strhex(response)}')

    len_ind = 0 if not modbus else 3

    if modbus:
        print(f'add (endereço): {response[0]:02x}')
        print(f'fun (função): {response[1]:02x}')
        print(f'op = {const_nome(response[2])}')

    if operation in (SEND_STRING, REQUEST_STRING):
        lenght = response[len_ind]
        value = bytes_to_string(response[len_ind + 1: len_ind + 1 + lenght])

        print(f'Tamanho: {lenght} — String: {value}')
    elif operation in (SEND_FLOAT, REQUEST_FLOAT):
        value = bytes_to_float(response[len_ind:-2])

        print(f'Float recebido: {value}')
    elif operation in (SEND_INT, REQUEST_INT):
        value = bytes_to_int(response[len_ind:-2])

        print(f'Inteiro recebido: {value}')
    else:
        print('ERRO: Pacote inválido recebido')

    if modbus:
        print(f'CRC = {_strhex(response[-2:])}')

def _strhex(s):
    return "b'" + re.sub(r'.', lambda m: f'\\x{ord(m.group(0)):02x}', s.decode('latin1')) + "'"
