import serial
import time

VAR_LENGHT = 0

def _open_serial():
    return serial.Serial(
        port='/dev/serial0',
        baudrate=115200,
        timeout=1,
        bytesize=serial.EIGHTBITS, # Bits de dados (por byte)
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,

        # Controle de fluxo
        xonxoff=False,
        rtscts=False,
        dsrdtr=False
    )


# Envia um pacote e recebe a resposta
def connect(send_data : bytes, response_lenght : int, max_retries : int, modbus=False):
    ser = _open_serial()
    ser.write(send_data)

    response = b''
    len_ind = 0 if not modbus else 3

    for attempt in range(max_retries):
        response = b''
        try:
            if(response_lenght <= VAR_LENGHT):
                response = ser.read(1 if not modbus else len_ind+1)

                response += ser.read(response[len_ind] + (2 if modbus else 0))
            else:
                response = ser.read(response_lenght + (5 if modbus else 0))
        except serial.SerialTimeoutException:
            print(f'ERRO: Timeout')
        except serial.SerialException as e:
            print(f'ERRO: Não foi possível se comunicar com a porta serial, tentando novamente... {attempt + 1}: {e}')
            try:
                ser.close()
                time.sleep(0.5)
                ser.open()
            except:
                pass
        else:
            break
        if attempt < max_retries - 1:
            time.sleep(0.1)

    ser.close()
    return response
