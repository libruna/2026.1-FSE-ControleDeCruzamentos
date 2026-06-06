import socket
import threading
import time

from config.network import HOST, PORT

vehicle_data = {} # Guarda as contagens
connected_clients = {} # Guarda os sockets

def handle_client(client_socket, client_address):
    client_id_local = None
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            
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
        
        print(f'Servidor Central operando em [{HOST}:{PORT}]')
    
        # Thread para interface do usuário
        while True:
            print('\n------- MENU -------')
            print('1 - Visualizar informações de tráfego')
            print('2 - Modo Noturno')
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
                    send_command('cruzamento_1', 'night_mode')
                elif submenu_option == '2':
                    send_command('cruzamento_2', 'night_mode')
                elif submenu_option == '0':
                    print('\nEncerrando...')
                    break

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