import socket
import threading
import json

from config.network import HOST, PORT

import config.modbus_lpr as modbus
from uart.uart_connection import *
from uart.protocol_simple import make_payload
from uart.protocol_modbus import wrap_modbus
from config.road import ROAD_MAP
from uart.parser import *
from utils import *

from os import path, mkdir
from collections import deque
from datetime import datetime

traffic_data = {} # Guarda as contagens por cruzamento 
connected_clients = {} # Guarda os sockets
license_plate_query_requests = deque() # fila de requisições lpr

log_folder = path.join(get_project_root(), 'log')
infractions_log_file = path.join(log_folder, 'infractions.txt')
status_file = path.join(log_folder, 'SYSTEM_STATUS')
traffic_log_file = path.join(log_folder, 'traffic_history.txt') # histórico de veículos por cruzamento e via

class Status:
    def __init__(self, bytes):
        self.active = 0
        self.road = 0
        self.direction = 0
        self.intersection_id = 0
        self.vehicle_type = 0
        self.signal_group = 0
        self.timed_out = 0
        self.unattended_count = 0
        self.elapsed_s_x10 = 0
        self.max_time_s_x10 = 0
        self.night_mode = 0
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
    
    def __repr__(self):
        return f"""\
{'emergência ativa' if self.active == 1 else 'sem emergência'}
road: {'principal' if self.road == 1 else 'auxiliar' if self.road == 2 else 'nenhuma'}
direction: {'leste' if self.direction == 1 else 'oeste' if self.direction == 2 else 'norte' if self.direction == 3 else 'sul' if self.direction == 4 else 'nenhuma'}
intersection_id: {'ambos / n/' if self.intersection_id == 0 else '1' if self.intersection_id == 1 else '2'}
vehicle_type: {'nenhum' if self.vehicle_type == 0 else 'ambulância' if self.vehicle_type == 1 else 'bombeiros' if self.vehicle_type == 2 else 'policia'}
signal_group: {self.signal_group}
emergência: {'OK' if self.timed_out == 0 else 'Falha'}
emergências não atendidas: {self.unattended_count}
tempo de emergência: {self.elapsed_s_x10/10:.1f}s
tempo maximo de emergência: {self.max_time_s_x10/10:.1f}s
{'noite' if self.night_mode == 1 else 'dia'}"""

system_status : Status

def handle_client(client_socket, client_address):
    client_id_local = None
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            messages = data.strip().split('\n')

            for msg in messages:
                if not msg:
                    continue

                if msg.startswith("INFRACTION"):
                    parts = msg.split(':')
                    
                    if len(parts) == 4:
                        cruz_num = parts[1]
                        s_id = parts[2]
                        speed = float(parts[3])

                        client_key = f"cruzamento_{cruz_num}"

                        print(f"\n[INFO] Cruzamento {client_key.upper()} -> ({s_id}) detectou uma infração: carro a {speed:.2f} km/h")

                        if client_key not in traffic_data:
                            traffic_data[client_key] = {'total_infractions': 0, 'sensors': {}}
                        
                        traffic_data[client_key]['total_infractions'] += 1

                        mapadd = {
                            'sensor_1': modbus.LPR1,
                            'sensor_2': modbus.LPR2,
                            'sensor_3': modbus.LPR3,
                            'sensor_4': modbus.LPR4
                        }
                        query_license_plate(cruz_num, s_id, modbus.get_camera_from_sensor(parts[2]), parts[3])
                        
                elif msg.count(':') == 3:
                    client_id, s_id, count, avg_speed = msg.split(':')
                    client_id_local = client_id
                    count_int = int(count)
                    speed_float = float(avg_speed)
                    
                    if client_id not in connected_clients:
                        connected_clients[client_id] = client_socket

                    if client_id not in traffic_data:
                        traffic_data[client_id] = {'total_infractions': 0, 'sensors': {}}

                    if s_id not in traffic_data[client_id]['sensors']:
                        traffic_data[client_id]['sensors'][s_id] = {
                            'count': 0,
                            'avg_speed': 0.0,
                            'flux_history': deque()
                        }
                    
                    sensor_node = traffic_data[client_id]['sensors'][s_id]

                    old_count = sensor_node['count']
                    sensor_node['count'] = count_int
                    sensor_node['avg_speed'] = speed_float
                    
                    now = time.time()
                    queue = sensor_node['flux_history']
                    queue.append((now, count_int))

                    if old_count > 0 and count_int > old_count:
                        new_vehicles = count_int - old_count
                        for _ in range(new_vehicles):
                            log_vehicle_history(client_id, s_id)
                    
                    while queue and (now - queue[0][0]) > 60:
                        queue.popleft()
            
    except Exception as e:
        print(f"\n[ERRO] Falha ao processar dados do {client_id_local} no Servidor Central: {e}")
    finally:
        # Remove da lista de clientes ativos ao desconectar
        if client_id_local in connected_clients:
            print(f'\n[INFO] Cliente {client_id_local} desconectado')
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
            print(f'\n[SUCESSO] Comando "{command.strip()}" enviado para {client_id}')
        except Exception as e:
            print(f'\n[ERRO] Falha ao enviar comando para {client_id}: {e}')
    else:
        print(f'\n[INFO] {client_id} não está conectado')

class LicensePlateQuery:
    def __init__(self, cruz_num, s_id, camera_addr, speed):
        self.timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.cruz_num = cruz_num
        self.s_id = s_id
        self.camera_addr = camera_addr
        self.speed = speed
        self.completed = False
        self.license_plate = ''
        self.confidence = -1

    def complete(self, bytes):
        self.completed = True
        lenght = len(bytes)
        if lenght >= 7:
            self.license_plate = bytes_to_string(bytes[0:7])
        if lenght >= 10:
            self.confidence = bytes_to_int(b'\x00\x00\x00' + bytes[9:10], True)

    def complete_as_empty(self):
        self.completed = True

    def error(self):
        return self.completed and (not self.license_plate or self.confidence == -1)

    def __repr__(self):
        return f'License Plate: {self.license_plate}, {self.confidence}%' if self.completed else f'FAILED QUERY'

def query_license_plate(cruz_num, s_id, camera_addr, speed):
    global license_plate_query_requests
    lpq = LicensePlateQuery(cruz_num, s_id, camera_addr, speed)
    license_plate_query_requests.append(lpq)

def get_licence_plate(lpq : LicensePlateQuery):
    """
    chamado pelo modbus_handler, use query_license_plate()
    """

    camera_addr = lpq.camera_addr

    pl1 = make_payload(b'\x01\x00\x01\x00\x02\x01\x00', modbus.MATRICULA)
    pl1 = wrap_modbus(camera_addr, modbus.WRITE, pl1)

    ser = open_serial(0.5)

    ser.write(pl1)

    response1 = get_response(ser, 4, 1, modbus=True, has_subfunction=False)
    cam_status = ''

    while cam_status not in ['ok', 'err']:
        pl2 = make_payload(b'\x00\x00\x01\x00', modbus.MATRICULA)
        pl2 = wrap_modbus(camera_addr, modbus.READ, pl2)

        ser.write(pl2)

        response2 = get_response(ser, VAR_LENGHT, 1, modbus=True, has_subfunction=False)

        if len(response2) < 5: continue

        if response2[4:5] == b'\x02': cam_status = 'ok'
        elif response2[4:5] == b'\x03': cam_status = 'err'

    pl3 = make_payload(b'\x00\x00\x08\x00', modbus.MATRICULA)
    pl3 = wrap_modbus(camera_addr, modbus.READ, pl3)

    ser.write(pl3)
    response3 = get_response(ser, VAR_LENGHT, 1, modbus=True, has_subfunction=False)

    if cam_status == 'err':
        if len(response3) >= 3:
            print(f'[ERRO]: câmera LPR retornou código de erro: {response3[-3]}')
        else:
            print(f'[ERRO]: falha na câmera LPR, ou na comunicação serial')
    else:
        if len(response3) >= 18:
            lpq.complete(response3[7:18])
        else:
            print(f'[ERRO]: falha na comunicação com a câmera LPR')

    pl4 = make_payload(b'\x01\x00\x01\x00\x02\x00\x00', modbus.MATRICULA) # reset trigget
    pl4 = wrap_modbus(camera_addr, modbus.WRITE, pl4)

    ser.write(pl4)

    ser.readall()

    ser.close()


def get_status():
    pl = make_payload(b'\x00\x00\x0B\x00', modbus.MATRICULA) # solicita os 11 registradores 
    pl = wrap_modbus(modbus.STATE, modbus.READ, pl)

    ser = open_serial(0.5) # abre conexão serial com timeout de 500ms

    ser.write(pl)

    response = get_response(ser, VAR_LENGHT, 5, modbus=True, has_subfunction=False)
#    print(strhex(response))

    ser.close()
    return response

def log_infraction(lpq : LicensePlateQuery):
    inf = f'{datetime.now()} - {modbus.get_sensor_from_camera(lpq.camera_addr)} - {lpq} - {lpq.speed}Km/h\n' 
    try:
        if path.exists(infractions_log_file):
            with open(infractions_log_file, 'a') as f:
                f.write(inf)
        else:
            if not path.isdir(log_folder):
                mkdir(log_folder)
            with open(infractions_log_file, 'w') as f:
                f.write(inf)
    except Exception as e:
        print(f"[ERRO]: Failure to log infraction: {e}")
    print('[INFRACTION]: ' + inf)

def log_vehicle_history(client_id, s_id):
    #print(f'\n[INFO] Registrando passagem de veículo detectada no {s_id} do {client_id}...')
    intersection_name = ROAD_MAP.get(client_id, {}).get(s_id, s_id)
    
    log_entry = f'{datetime.now()} - {client_id.upper()} - {intersection_name} - Veículo detectado\n'
    
    try:
        if path.exists(traffic_log_file):
            with open(traffic_log_file, 'a') as f:
                f.write(log_entry)
        else:
            if not path.isdir(log_folder):
                mkdir(log_folder)
            with open(traffic_log_file, 'w') as f:
                f.write(log_entry)
    except Exception as e:
        print(f"[ERRO]: Falha ao salvar histórico de passagens de veículos: {e}")

def modbus_handler(status_cooldown : float):
    global system_status

    last_emergency_active = None
    last_night_mode = None

    while True:
        if license_plate_query_requests:
            lpq = license_plate_query_requests.popleft()
            get_licence_plate(lpq)
            log_infraction(lpq)

        status_bytes = get_status()
        if not status_bytes:
            print("[ERRO] falha ao obter estado do sistema")
        else:
            status_bytes = status_bytes[3:-2]
            system_status = Status(status_bytes)

            current_active = system_status.active
            current_night_mode = system_status.night_mode

            if last_emergency_active is None or last_night_mode is None:
                last_emergency_active = current_active
                last_night_mode = current_night_mode
                time.sleep(status_cooldown)
                continue 

            if current_active in [0, 1] and current_active != last_emergency_active:
                if current_active == 1:
                    sig_group = system_status.signal_group
                    inter_id = system_status.intersection_id
                    
                    print(f"\n[INFO] Veículo de emergência detectado. Liberando sinal {sig_group} no cruzamento {inter_id}")
                    
                    cmd = f'EMERGENCY_ON:{sig_group}\n'
                    if inter_id in [0, 1]: send_command('cruzamento_1', cmd)
                    if inter_id in [0, 2]: send_command('cruzamento_2', cmd)
                        
                elif current_active == 0:
                    print("\n[INFO] Emergência encerrada. Retornando operação normal...")
                    cmd = 'EMERGENCY_OFF\n'
                    send_command('cruzamento_1', cmd)
                    send_command('cruzamento_2', cmd)
                    
                last_emergency_active = current_active
                
            if current_night_mode in [0, 1] and current_night_mode != last_night_mode:
                if current_night_mode == 1:
                    print("\n[INFO] MODBUS -> Modo noturno ativado")
                    send_command('cruzamento_1', 'NIGHT_MODE_ON\n')
                    send_command('cruzamento_2', 'NIGHT_MODE_ON\n')
                elif current_night_mode == 0:
                    print("\n[INFO] MODBUS -> Modo noturno desativado")
                    send_command('cruzamento_1', 'NIGHT_MODE_OFF\n')
                    send_command('cruzamento_2', 'NIGHT_MODE_OFF\n')
                    
                last_night_mode = current_night_mode
    
        time.sleep(status_cooldown)

def show_traffic_info():
    print('\n======================== Monitoramento ========================')

    if not traffic_data:
        print('\nNenhum dado de cruzamento recebido até o momento.')
    else:
        for client_id, intersection_node in traffic_data.items():
            print(f'\n{client_id.upper()}')
            
            for s_id, sensor_node in intersection_node['sensors'].items():
                count = sensor_node['count']
                avg_speed = sensor_node['avg_speed']
                queue = sensor_node['flux_history']
                
                if len(queue) >= 2:
                    flux_per_minute = queue[-1][1] - queue[0][1]
                else:
                    flux_per_minute = 0                
                
                print(f'   - {s_id}: {count} carros no total | {flux_per_minute} carros/min  | Vm = {avg_speed:.1f} km/h')
            
            total_infractions = intersection_node['total_infractions']
            print(f'   -> Total de infrações de velocidade = {total_infractions}')
    print('=================================================================\n')

def manage_night_mode():
    while True:
        print('\n=============== MODO NOTURNO ===============')
        print('1 - ATIVAR no Cruzamento 1')
        print('2 - DESATIVAR no Cruzamento 1')
        print('3 - ATIVAR no Cruzamento 2')
        print('4 - DESATIVAR no Cruzamento 2')
        print('0 - Voltar')
        print('==============================================\n')

        option = input('Escolha uma opção: ')
        
        if option == '1':
            send_command('cruzamento_1', 'NIGHT_MODE_ON\n')
        elif option == '2':
            send_command('cruzamento_1', 'NIGHT_MODE_OFF\n')
        elif option == '3':
            send_command('cruzamento_2', 'NIGHT_MODE_ON\n')
        elif option == '4':
            send_command('cruzamento_2', 'NIGHT_MODE_OFF\n')
        elif option == '0':
            break
        else:
            print('\n[ERRO] Opção inválida')

def manual_control_traffic_lights():
    while True:
        print('\n=============== CONTROLE MANUAL ===============')
        print('0 - Estado 0 (Amarelo  | Amarelo) -> ! Modo noturno !')
        print('1 - Estado 1 (Verde    | Vermelho)')
        print('2 - Estado 2 (Amarelo  | Vermelho)')
        print('3 - Estado 3 (Amarelo  | Vermelho)')
        print('4 - Estado 4 (Vermelho | Vermelho)')
        print('5 - Estado 5 (Vermelho | Verde)')
        print('6 - Estado 6 (Vermelho | Amarelo)')
        print('7 - Estado 7 (Vermelho | Amarelo)')
        print('9 - Voltar')
        print('==================================================\n')
        
        option = input('\nEscolha uma opção: ')
        
        if option == '0':
            manage_night_mode()  
        elif option in [str(i) for i in range(8)]:
            cmd = f'MANUAL_STATE:{option}\n'
            send_command('cruzamento_1', cmd)
            send_command('cruzamento_2', cmd)
            print(f'\n[MODO MANUAL] Ativado -> Alterando os cruzamentos para o estado {option}')
        elif option == '9':
            send_command('cruzamento_1', 'MANUAL_OFF\n')
            send_command('cruzamento_2', 'MANUAL_OFF\n')
            print('\n[MODO MANUAL] Desativado -> Sistema retornado para modo automático')
            break
        else:
            print('\n[ERRO] Opção inválida')

def start_server():
    global system_status

    if path.exists(status_file):
        print('[INFO] Carregando estado anterior')
        try:
            with open(status_file, 'r') as f:
                l = f.readline()
                system_status = json.loads(l)
        except Exception as e:
            print(f'[ERRO] Falha ao carregar estado anterior + {e}')
    else:
        print(f'[ERRO] O arquivo de estado não foi encontrado')
        

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    while True:
        try:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()

            # Thread que fica escutando a rede
            accept_thread = threading.Thread(target=accept_connections, args=(server_socket,))
            accept_thread.daemon = True
            accept_thread.start()

            # Thread que recebe o estado do sistema e maneja o modbus
            status_thread = threading.Thread(target=modbus_handler, args=(0.25,), daemon=True)
            status_thread.start()

            print(f'\n[INFO] Servidor Central ouvindo em [{HOST}:{PORT}]')
        
            # Thread para interface do usuário
            while True:
                print('\n================ MENU ================')
                print('1 - Visualizar informações de tráfego')
                print('2 - Visualizar estado do sistema')
                print('3 - Controle manual de estados')
                print('0 - Sair')
                print('=======================================\n')
                
                option = input('\nEscolha uma opção: ')
                
                if option == '1':
                    show_traffic_info()
                elif option == '2':
                    print(f'\n============== ESTADO DO SISTEMA ==============')
                    print(system_status)
                    print('\n======================================================\n') 
                elif option == '3':
                    manual_control_traffic_lights()
                elif option == '0':
                    print('\nEncerrando...')
                    break
                else:
                    print('\nOpção inválida')
        except KeyboardInterrupt:
            print(f'\nEncerrando...')
            break
        except Exception as e:
            print(f'\n[FATAL] {e}')
            print(f'[INFO] Tentando reconexão...')
        else:
            break
        finally:
            print(f'Salvando estado atual para \"' + status_file + '\"')
            if path.isdir(log_folder):
                with open(status_file, 'w') as f:
                    f.write(json.dumps(system_status.__dict__))
            else:
                mkdir(log_folder)
                with open(status_file, 'w') as f:
                    f.write(json.dumps(system_status.__dict__))
            server_socket.close()

if __name__ == '__main__':
    start_server()
