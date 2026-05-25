from uart import protocol_simple, protocol_modbus

def menu_uart():
    while True:
        print("\n------- UART -------")
        print("1 - Protocolo Simplificado")
        print("2 - Protocolo MODBUS")
        print("0 - Voltar")

        option = input("Escolha: ")

        if option == "1":
            menu_simple_protocol()

        elif option == "2":
            print("todo")
            #menu_modbus_protocol()

        elif option == "0":
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

        if option == '1':
            protocol_simple.request_int()

        elif option == '2':
            protocol_simple.request_float()

        elif option == '3':
            protocol_simple.request_string()

        elif option == '4':
            value = int(input('Digite um inteiro: '))
            protocol_simple.send_int(value)

        elif option == '5':
            value = float(input('Digite um float: '))
            protocol_simple.send_float(value)

        elif option == '6':
            value = input('Digite uma string: ')
            protocol_simple.send_string(value)

        elif option == '0':
            print('Encerrando...')
            break

        else:
            print('Opção inválida')
