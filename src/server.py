import socket
import threading

from config.network import HOST, PORT

import config.modbus_lpr as modbus
from uart.uart_connection import *
from uart.protocol_simple import make_payload
from uart.protocol_modbus import wrap_modbus
from uart.parser import *

from collections import deque

vehicle_data = {} # Guarda as contagens
connected_clients = {} # Guarda os sockets
license_plate_query_requests = deque() # fila de requisições lpr

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

                    mapadd = {
                        'sensor_1': modbus.LPR1,
                        'sensor_2': modbus.LPR2,
                        'sensor_3': modbus.LPR3,
                        'sensor_4': modbus.LPR4
                    }
                    th = threading.Thread(target=query_license_plate, args=(mapadd[data[2]],),daemon=True)
                    th.start()
                
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

class LicensePlateQuery:
    def __init__(self, camera_addr):
        self.camera_addr = camera_addr
        self.completed = False
        self.license_plate = ''
        self.confidence = -1

    def complete(self, bytes):
        self.completed = True
        lenght = len(bytes)
        if lenght >= 16:
            self.license_plate = bytes[1:16:2]
        if lenght >= 18:
            self.confidence = bytes_to_int(b'\x00\x00' + bytes[16:18], True)

    def complete_as_empty(self):
        self.completed = True

    def error(self):
        return self.completed and (not self.license_plate or self.confidence == -1)

    def __repr__(self):
        return f'License Plate: {self.license_plate}, {self.confidence}%' if self.completed else f'INCOMPLETE LICENSE PLATE QUERY'

def query_license_plate(camera_addr):
    global license_plate_query_requests
    lpq = LicensePlateQuery(camera_addr)
    license_plate_query_requests.append(lpq)
    while not lpq.completed:
        pass
    print(lpq)

def get_licence_plate(lpq : LicensePlateQuery):
    """
    chamado pelo modbus_handler, use query_license_plate()
    """

    camera_addr = lpq.camera_addr

    pl = make_payload(b'\x01\x00\x01\x00\x02\x01\x00', modbus.MATRICULA)
    pl = wrap_modbus(camera_addr, modbus.WRITE, pl)

    ser = open_serial(0.5)

    ser.write(pl)

    response = get_response(ser, 4, 1, modbus=True, has_subfunction=False)

    cam_status = ''

    while cam_status not in ['ok', 'err']:
        pl = make_payload(b'\x00\x00\x01\x00', modbus.MATRICULA)
        pl = wrap_modbus(camera_addr, modbus.READ, pl)

        ser.write(pl)

        response = get_response(ser, VAR_LENGHT, 1, modbus=True, has_subfunction=False)

        if response[4:5] == b'\x02': cam_status = 'ok'
        elif response[4:5] == b'\x03': cam_status = 'err'

    pl = make_payload(b'\x00\x00\x08\x00', modbus.MATRICULA)
    pl = wrap_modbus(camera_addr, modbus.READ, pl)

    ser.write(pl)

    response = get_response(ser, VAR_LENGHT, 1, modbus=True, has_subfunction=True)


    if cam_status == 'err':
        print(f'[LPR ERRO]: {response[-3]}')
        lpq.complete_as_empty()
    else:
        lpq.complete(response[3:-2])

    ser.close()


def get_status():
    pl = make_payload(b'\x00\x00\x0B\x00', modbus.MATRICULA) # solicita os 11 registradores 
    pl = wrap_modbus(modbus.STATE, modbus.READ, pl)

    ser = open_serial(0.5) # abre conexão serial com timeout de 500ms

    ser.write(pl)

    response = get_response(ser, VAR_LENGHT, 5, modbus=True, has_subfunction=False)
#    print(strhex(response))

    ser.close()
    return response[2:-2] # exclui o modbus e crc

def modbus_handler(status_cooldown : float):
    global system_status
    while True:
        if license_plate_query_requests:
            print('atendendo request')
            lpq = license_plate_query_requests.popleft()
            get_licence_plate(lpq)

        status_bytes = get_status()[1:] # exclui o bytecount
        if status_bytes:
            system_status = Status(status_bytes)
        else:
            print('[ERRO]: Falha ao receber estado')
    
        time.sleep(status_cooldown)
    

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

        # Thread que recebe o estado do sistema e maneja o modbus
        status_thread = threading.Thread(target=modbus_handler, args=(0.25,), daemon=True)
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
{'emergência ativa' if system_status.active == 1 else 'sem emergência'}
road: {'principal' if system_status.road == 1 else 'auxiliar' if system_status.road == 2 else 'nenhuma'}
direction: {'leste' if system_status.direction == 1 else 'oeste' if system_status.direction == 2 else 'norte' if system_status.direction == 3 else 'sul' if system_status.direction == 4 else 'nenhuma'}
intersection_id: {'ambos / n/' if system_status.intersection_id == 0 else '1' if system_status.intersection_id == 1 else '2'}
vehicle_type: {'nenhum' if system_status.vehicle_type == 0 else 'ambulância' if system_status.vehicle_type == 1 else 'bombeiros' if system_status.vehicle_type == 2 else 'policia'}
signal_group: {system_status.signal_group}
emergência: {'OK' if system_status.timed_out == 0 else 'Falha'}
emergências não atendidas: {system_status.unattended_count}
tempo de emergência: {system_status.elapsed_s_x10/10:.1f}s
tempo maximo de emergência: {system_status.max_time_s_x10/10:.1f}s
{'noite' if system_status.night_mode == 1 else 'dia'}
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
