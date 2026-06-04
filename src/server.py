import socket

from config.network import HOST, PORT

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.bind((HOST, PORT))
server.listen()

print(f'Servidor Central ouvindo em {HOST}:{PORT}')

while True:
    client, address = server.accept()

    print(f'Nova conexão recebida de {address[0]}:{address[1]}')

    data = client.recv(1024)
    print(f'Dados recebidos: {data.decode()}')