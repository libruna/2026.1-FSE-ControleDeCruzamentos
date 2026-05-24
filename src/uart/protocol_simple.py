# protocolo 1
import serial
from numpy import float32
import struct

def raw_bytes_to_int(bytes):
    res = 0
    for i in range(len(bytes)):
        res += bytes[len(bytes) - 1 - i] * 10**i
    return res


#ser = serial.Serial(
#     port='/dev/serial0',
#     baudrate=115200,
#     timeout=1,
#     bytesize=serial.EIGHTBITS, # Bits de dados (por byte)
#     parity=serial.PARITY_NONE,
#     stopbits=serial.STOPBITS_ONE,

#     # Controle de fluxo
#     xonxoff=False,
#     rtscts=False,
#     dsrdtr=False
# )

# while not entrada:
    # entrada = ser.read(7) # CMD + D1-D6

# entrada = b'\xa1\x06\x05\x04\x03\x02\x01'
# entrada = b'\xa2\x06\x05\x04\x03\x02\x01'
# entrada = b'\xa3\x06\x05\x04\x03\x02\x01'
# entrada = b'\xb1\x00\x00\x00\x05\x06\x05'
# entrada = b'\xb2\xd0\x0f\x49\x40\x06\x05'
# entrada = b'\xb3\x05\x48\x65\x6c\x6c\x6f'

e = [entrada[i:i+1] for i in range(7)] # só para facilitar a comparação

# ENTRADA ADICIONAL
if e[0] == b'\xb3':
    n = raw_bytes_to_int([entrada[1]]) + 1
    # cont = read(n)
    # if not cont:
    #     # TODO: Erro
    entrada += b'\x06\x05\x04\x03\x02\x01'
    e = [entrada[i:i+1] for i in range(7+n)]

elif e[0] == b'\xb1' or e[0] == b'\xb2' or e[0] == b'\xb3':
    # cont += ser.read(4)
    # if not cont:
    #     # TODO: erro que faltou info
    # entrada += cont
    entrada += b'\x04\x03\x02\x01'
    e = [entrada[i:i+1] for i in range(11)]


print(f'entrada: {entrada}')

# OPERAÇÕES
if e[0] == b'\xa1': # Solicita inteiro
    matricula = raw_bytes_to_int(entrada[1:])

    print(f'matricula: {matricula}')
    print(f'saída: {matricula.to_bytes(4, byteorder='big')}')

    #ser.write(matricula.to_bytes(4, byteorder='big'))

elif e[0] == b'\xa2': # Solicita float
    matricula = float(raw_bytes_to_int(entrada[1:]))

    bytearr = struct.pack('f', matricula) # talvez esteja ao contrário

    print(f'matricula: {matricula}')
    print(f'saída: {bytearr}')

    #ser.write(bytearr)

elif e[0] == b'\xa3': # Solicita string
    matricula = str(raw_bytes_to_int(entrada[1:]))

    print(f'matricula: "{matricula}"')
    print(f'saída: {len(matricula).to_bytes(1) + matricula.encode('ascii')}')

    #ser.write(len(matricula).to_bytes(1, signed=False) + matricula.encode('ascii'))

elif e[0] == b'\xb1': # Envia inteiro
    mult = raw_bytes_to_int(entrada[1:5])
    matricula = raw_bytes_to_int(entrada[5:])
    res = mult * (matricula % 10)

    print(f'matricula: {matricula}')
    print(f'mult: {mult}')
    print(f'saída: {res.to_bytes(4, byteorder='big')}')

    #ser.write(res.to_bytes(4, byteorder='big', signed=False))

elif e[0] == b'\xb2': # Envia float
    mult = struct.unpack('f', entrada[1:5])[0]
    matricula = raw_bytes_to_int(entrada[5:])
    res = float(matricula % 10) * mult

    bytearr = struct.pack('f', res)

    print(f'matricula: {matricula}')
    print(f'mult: {mult}')
    print(f'saída: {bytearr}')

    #ser.write(bytearr)

elif e[0] == b'\xb3': # Envia string
    n = raw_bytes_to_int([entrada[1]])
    string = entrada[2:2+n].decode('ascii')
    matricula = raw_bytes_to_int(entrada[2+n:])

    s = 'Resposta da UART: ' + string


    print(f'matricula: {matricula}')
    print(f'string: {string}')
    print(f'saida: {len(s).to_bytes(1) + s.encode('ascii')}')

    # ser.write(len(s).to_bytes(1) + s.encode('ascii'))
    

#ser.close()


