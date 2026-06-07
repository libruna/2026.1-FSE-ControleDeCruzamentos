import socket
import threading

from config.network import HOST, PORT

import config.modbus_lpr as modbus
from uart.uart_connection import *
from uart.protocol_simple import make_payload
from uart.protocol_modbus import wrap_modbus
from uart.parser import *

vehicle_data = {} # Guarda as contagens
connected_clients = {} # Guarda os sockets

class Status:
    def __init__(self, bytes):
        lenght = len(bytes)
        if lenght >= 2:
            self.active = bytes_to_int(b'\x00\x00' + bytes[0:2], True)
        if lenght >= 4:
            self.road = bytes_to_int(b'\x00\x00' + bytes[2:4], True)
        if lenght >= 6:
            self.direction = bytes_to_int(b'\x00\x00' + bytes[4:6], True)
        if lenght >= 8:
            self.intersection_id = bytes_to_int(b'\x00\x00' + bytes[6:8], True)
        if lenght >= 10:
            self.vehicle_type = bytes_to_int(b'\x00\x00' + bytes[8:10], True)
        if lenght >= 12:
            self.signal_group = bytes_to_int(b'\x00\x00' + bytes[10:12], True)
        if lenght >= 14:
            self.timed_out = bytes_to_int(b'\x00\x00' + bytes[12:14], True)
        if lenght >= 16:
            self.unattended_count = bytes_to_int(b'\x00\x00' + bytes[14:16], True)
        if lenght >= 18:
            self.elapsed_s_x10 = bytes_to_int(b'\x00\x00' + bytes[16:18], True)
        if lenght >= 20:
            self.max_time_s_x10 = bytes_to_int(b'\x00\x00' + bytes[18:20], True)
        if lenght >= 22:
            self.night_mode = bytes_to_int(b'\x00\x00' + bytes[20:22], True)

system_status: Status

def handle_client(client_socket, client_address):
    client_id_local = None
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            if data.startswith("INFRACTION"):
                parts = data.split(':')
                
                if len(parts) == 4:
                    # multa
                    print(f"\n[INFO] Cruzamento {parts[1]} ({parts[2]}) detectou uma infração: carro a {parts[3]} km/h!")
                
                continue
            
            if data.count(':') == 2:
                client_id, sensor_id, count = data.split(':')
                client_id_local = client_id
                
                if client_id not in connected_clients:
                    connected_clients[client_id] = client_socket
                
                if client_id not in vehicle_data:
                    vehicle_data[client_id] = {}
                    
                vehicle_data[client_id][sensor_id] = int(count)
            
    except Exception as e:
        pass
    finally:
        # Remove da lista de clientes ativos ao desconectar
        if client_id_local in connected_clients:
            del connected_clients[client_id_local]
        client_socket.close()

def accept_connections(server_socket):
    # Thread em background para aceitar novos cruzamentos
    while True:
        try:
            client, address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client, address))
            client_thread.daemon = True
            client_thread.start()
        except Exception:
            break

def send_command(client_id, command):
    if client_id in connected_clients:
        try:
            connected_clients[client_id].sendall(command.encode('utf-8'))
            print(f'\n[SUCESSO] Comando "{command}" enviado para {client_id}.')
        except Exception as e:
            print(f'\n[ERRO] Falha ao enviar comando para {client_id}: {e}')
    else:
        print(f'\n[INFO] {client_id} não está conectado.')

def show_traffic_info():
    print('\n------- Monitoramento -------')

    if not vehicle_data:
        print('\nNenhum dado de cruzamento recebido até o momento.')
    else:
        for client_id, sensors in vehicle_data.items():
            print(f'{client_id.upper()}')
            for s_id, count in sensors.items():
                print(f'   - {s_id}: {count} veículos')


def get_status():
    pl = make_payload(b'\x00\x00\x0B\x00', modbus.MATRICULA) # solicita os 11 registradores 
    pl = wrap_modbus(modbus.STATE, modbus.READ, pl)

    ser = open_serial(0.5) # abre conexão serial com timeout de 500ms

    ser.write(pl)

    response = get_response(ser, VAR_LENGHT, 5, modbus=True, has_subfunction=False)
#    print(strhex(response))

    ser.close()
    return response[2:-2] # exclui o modbus e crc

def status_listener(seconds : float):
    global system_status
    while True:
        status_bytes = get_status()[1:] # exclui o bytecount
        if status_bytes:
            system_status = Status(status_bytes)
        else:
            print('[ERRO]: Falha ao receber estado')
    
        time.sleep(seconds)

def start_server():
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        # Thread que fica escutando a rede
        accept_thread = threading.Thread(target=accept_connections, args=(server_socket,))
        accept_thread.daemon = True
        accept_thread.start()

        # Thread que recebe o estado do sistema
        status_thread = threading.Thread(target=status_listener, args=(1,), daemon=True)
        status_thread.start()

        print(f'\nServidor Central operando em [{HOST}:{PORT}]')
    
        # Thread para interface do usuário
        while True:
            print('\n------- MENU -------')
            print('1 - Visualizar informações de tráfego')
            print('2 - Modo Noturno')
            print('3 - Visualizar estado do sistema')
            print('0 - Sair')
            
            option = input('\nEscolha uma opção: ')
            
            if option == '1':
                show_traffic_info()
            elif option == '2':
                print('\n------- MODO NOTURNO -------')
                print('1 - Cruzamento 1')
                print('2 - Cruzamento 2')
                print('0 - Sair')

                submenu_option = input('\nEscolha uma opção: ')

                if submenu_option == '1':
                    send_command('cruzamento_1', 'NIGHT_MODE_ON')
                elif submenu_option == '2':
                    send_command('cruzamento_2', 'NIGHT_MODE_ON')
                elif submenu_option == '0':
                    print('\nEncerrando...')
                    break

            elif option == '3':
                print(f""" \
                    active: {system_status.active}
                    road: {system_status.road}
                    direction: {system_status.direction}
                    intersection_id: {system_status.intersection_id}
                    vehicle_type: {system_status.vehicle_type}
                    signal_group: {system_status.signal_group}
                    timed_out: {system_status.timed_out}
                    unnatended_count: {system_status.unattended_count}
                    elapsed_s_x10: {system_status.elapsed_s_x10}
                    max_time_s_x10: {system_status.max_time_s_x10}
                    night_mode: {system_status.night_mode}
                """)
            elif option == '0':
                print('\nEncerrando...')
                break
            else:
                print('\nOpção inválida')

    except Exception as e:
        print(f'\n[ERRO] : {e}')
    finally:
        server_socket.close()

if __name__ == '__main__':
    start_server()
