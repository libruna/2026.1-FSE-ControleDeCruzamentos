from urllib import response

from uart import protocol_simple, protocol_modbus
from uart.constants import *
from uart.parser import *
from uart.uart_connection import get_response, open_serial
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

            payload = _make_payload(operation)

            _interpret_sent_simple(payload, operation)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, 4, 5)
                _interpret_response(response, operation)

                ser.close()
            except Exception as e:
                print(e)

        elif option == '2':
            operation = REQUEST_FLOAT

            payload = _make_payload(operation)

            _interpret_sent_simple(payload, operation)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, 4, 5)
                _interpret_response(response, operation)

                ser.close()
            except Exception as e:
                print(e)

        elif option == '3':
            operation = REQUEST_STRING

            payload = _make_payload(operation)

            _interpret_sent_simple(payload, operation)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, VAR_LENGHT, 5)
                _interpret_response(response, operation)

                ser.close()
            except Exception as e:
                print(e)

        elif option == '4':
            operation = SEND_INT
            value = int_to_bytes(int(input('Digite um inteiro: ')))

            payload = _make_payload(operation, value)

            _interpret_sent_simple(payload, operation, value)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, 4, 5)
                _interpret_response(response, operation)

                ser.close()
            except Exception as e:
                print(e)

        elif option == '5':
            operation = SEND_FLOAT
            value = float_to_bytes(float(input('Digite um float: ')))

            payload = _make_payload(operation, value)

            _interpret_sent_simple(payload, operation, value)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, 4, 5)
                _interpret_response(response, operation)

                ser.close()
            except Exception as e:
                print(e)

        elif option == '6':
            operation = SEND_STRING
            value = string_to_bytes(input('Digite uma string: '))

            if not value:
                print('Entrada inválida')
                continue

            payload = _make_payload(operation, value)

            _interpret_sent_simple(payload, operation, value)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, VAR_LENGHT, 5)
                _interpret_response(response, operation)

                ser.close()
            except Exception as e:
                print(e)

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

            payload = _make_payload(operation)
            payload = protocol_modbus.wrap_modbus(ADDRESS, function, payload)

            _interpret_sent_modbus(payload, operation, function)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, 4, 5, True)
                _interpret_response(response, operation, True)

                ser.close()
            except Exception as e:
                print(e)

        elif option == '2':
            function = REQUEST_CODE
            operation = REQUEST_FLOAT

            payload = _make_payload(operation)
            payload = protocol_modbus.wrap_modbus(ADDRESS, function, payload)

            _interpret_sent_modbus(payload, operation, function)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, 4, 5, True)
                _interpret_response(response, operation, True)

                ser.close()
            except Exception as e:
                print(e)

        elif option == '3':
            function = REQUEST_CODE
            operation = REQUEST_STRING

            payload = _make_payload(operation)
            payload = protocol_modbus.wrap_modbus(ADDRESS, function, payload)

            _interpret_sent_modbus(payload, operation, function)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, VAR_LENGHT, 5, True)
                _interpret_response(response, operation, True)

                ser.close()
            except Exception as e:
                print(e)

        elif option == '4':
            function = SEND_CODE
            operation = SEND_INT

            value = int_to_bytes(int(input('Digite um inteiro: ')))

            payload = _make_payload(operation, value)
            payload = protocol_modbus.wrap_modbus(ADDRESS, function, payload)

            _interpret_sent_modbus(payload, operation, function, value)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, 4, 5, True)
                _interpret_response(response, operation, True)

                ser.close()
            except Exception as e:
                print(e)

        elif option == '5':
            function = SEND_CODE
            operation = SEND_FLOAT

            value = float_to_bytes(float(input('Digite um float: ')))

            payload = _make_payload(operation, value)
            payload = protocol_modbus.wrap_modbus(ADDRESS, function, payload)

            _interpret_sent_modbus(payload, operation, function, value)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, 4, 5, True)
                _interpret_response(response, operation, True)

                ser.close()
            except Exception as e:
                print(e)

        elif option == '6':
            function = SEND_CODE
            operation = SEND_STRING

            value = string_to_bytes(input('Digite uma string: '))

            if not value:
                print('Entrada inválida')
                continue

            payload = _make_payload(operation, value)
            payload = protocol_modbus.wrap_modbus(ADDRESS, function, payload)

            _interpret_sent_modbus(payload, operation, function, value)

            try:
                ser = open_serial()
                ser.write(payload)

                response = get_response(ser, payload, VAR_LENGHT, 5, True)
                _interpret_response(response, operation, True)

                ser.close()
            except Exception as e:
                print(e)

        elif option == '0':
            print('Encerrando...')
            break

        else:
            print('Opção inválida')

def _interpret_sent_simple(payload, operation, value = b''):

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
        elif(len(value) == 2):
            print(f'                    ^   ^   ^str-^  ^------matrícula-----^')
        else:
            print(f'                    ^   ^   ^--{"str".center((len(value)-2) * 4, "-")}--^  ^------matrícula-----^')
        print(f'                    op len {"str" if len(value) == 1 else "   "}                                                   \n')
        print(f'op = {const_nome(operation)}')
        print(f'len (tamanho) = {len(value)}')
        print(f'str = {bytes_to_string(value)}')
        print(f'matricula = {raw_bytes_to_int(MATRICULA)}')

    print()

def _interpret_sent_modbus(payload, operation, function, value = b'') -> bytes:
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
            print(f'                    ^   ^   ^   ^   ^   ^------matrícula-----  ^CRC-^')
        elif(len(value) == 2):
            print(f'                    ^   ^   ^   ^   ^str-^  ^------matrícula-----^  ^CRC-^')
        else:
            print(f'                    ^   ^   ^   ^   ^--{"str".center((len(value)-2) * 4, "-")}--^  ^------matrícula-----^  ^CRC-^')
        print(f'                   add fun  op len {"str" if len(value) == 1 else "   "}                                                      \n')
        print(f'add (endereço) = {_strhex(ADDRESS)}')
        print(f'fun (função) = {_strhex(function)}')
        print(f'op = {const_nome(operation)}')
        print(f'len (tamanho) = {len(value)}')
        print(f'str = {bytes_to_string(value)}')
        print(f'matricula = {raw_bytes_to_int(MATRICULA)}')
        print(f'crc = {_strhex(payload[-2:])}')

    print()

def _interpret_response(response, operation : bytes, modbus=False):
    print(f'Pacote recebido: {_strhex(response)}')

    len_ind = 0 if not modbus else 3

    if operation in (SEND_STRING, REQUEST_STRING):
        lenght = response[len_ind]
        value = bytes_to_string(response[len_ind + 1: len_ind + 1 + lenght])

        if modbus:
            if(lenght == 1):
                print(f'                     ^   ^   ^   ^   ^   ^CRC-^')
            if(lenght == 2):
                print(f'                     ^   ^   ^   ^   ^str-^   ^CRC-^')
            else:
                print(f'                     ^   ^   ^   ^   ^--{"str".center((lenght-2) * 4, "-")}--^  ^CRC-^')
            print(f'                    add fun  op len {"str" if lenght == 1 else "   "}                        \n')
            _modbus_interpret_header(response)
        else:
            if(lenght == 1):
                print(f'                     ^   ^')
            if(lenght == 2):
                print(f'                     ^   ^str-^')
            else:
                print(f'                     ^   ^--{"str".center((lenght-2) * 4, "-")}--^')
            print(f'                    len {"str" if lenght == 1 else "   "}\n')


        print(f'tamanho: {lenght} — string: {value}')
    elif operation in (SEND_FLOAT, REQUEST_FLOAT):
        value = bytes_to_float(response[len_ind: len(response) if not modbus else -2])

        if modbus:
            print(f'                     ^   ^   ^   ^---valor----^  ^CRC-^')
            print(f'                    add fun  op                        \n')
            _modbus_interpret_header(response)
        else:
            print(f'                     ^---valor----^\n')

        print(f'valor (float): {value}')
    elif operation in (SEND_INT, REQUEST_INT):
        value = bytes_to_int(response[len_ind:len(response) if not modbus else -2])

        if modbus:
            print(f'                     ^   ^   ^   ^---valor----^  ^CRC-^')
            print(f'                    add fun  op                        \n')
            _modbus_interpret_header(response)
        else:
            print(f'                     ^---valor----^\n')

        print(f'valor (inteiro): {value}')
    else:
        print('ERRO: pacote inválido recebido')

    if modbus:
        print(f'crc = {_strhex(response[-2:])}')

def _modbus_interpret_header(response):
    print(f'add (endereço): {_strhex(response[0:1])}')
    print(f'fun (função): {_strhex(response[1:2])}')
    opnome = const_nome(response[2:3])
    print(f'op = {'operação inválida' if not opnome else opnome}')

def _strhex(s):
    return "b'" + re.sub(r'.', lambda m: f'\\x{ord(m.group(0)):02x}', s.decode('latin1')) + "'"

def _make_payload(operation, value = b''):
    return protocol_simple.make_payload(operation, len(value).to_bytes(1) if operation == SEND_STRING else b'', value, MATRICULA)