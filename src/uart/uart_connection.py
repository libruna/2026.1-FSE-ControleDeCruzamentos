from email import header

import serial
import time
from config.modbus import MODBUS_ERRORS

VAR_LENGHT = 0

def open_serial(timeout = 1):
    return serial.Serial(
        port='/dev/serial0',
        baudrate=115200,
        timeout=timeout,
        bytesize=serial.EIGHTBITS, # Bits de dados (por byte)
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,

        # Controle de fluxo
        xonxoff=False,
        rtscts=False,
        dsrdtr=False
    )

# Envia um pacote e recebe a resposta
def get_response(ser, response_lenght: int, max_retries: int, modbus=False, has_subfunction = True):
    response = b''

    for attempt in range(max_retries):
        response = b''
        try:
            if modbus:
                header = ser.read(2)

                if len(header) < 2:
                    raise serial.SerialTimeoutException('Timeout ao receber resposta MODBUS')
                
                function_code = header[1]
                
                if function_code & 0x80:
                    rest = ser.read(2)
                    response = header + rest

                    print(f'Pacote recebido: {response}')

                    exception_code = response[2]

                    raise Exception(
                        f'ERRO MODBUS '
                        f'[{exception_code:#04x}]: '
                        f'{MODBUS_ERRORS.get(exception_code, "UNKNOWN ERROR")}'
                    )

                if response_lenght <= VAR_LENGHT:
                    rest = ser.read(2 if has_subfunction else 1)

                    response = header + rest

                    str_size = response[3 if has_subfunction else 2]

                    response += ser.read(str_size + 2)
                else:
                    response = header + ser.read(response_lenght + 3 if has_subfunction else 2)
            else:
                if response_lenght <= VAR_LENGHT:
                    response = ser.read(1)
                    response += ser.read(response[0])
                else:
                    response = ser.read(response_lenght)

        except serial.SerialTimeoutException:
            print(f'ERRO: Timeout')
            response = b''
        except serial.SerialException as e:
            print(f'ERRO: Não foi possível se comunicar com a porta serial, tentando novamente... {attempt + 1}: {e}')
            try:
                ser.close()
                time.sleep(0.5)
                ser.open()
            except:
                pass
            response = b''
        else:
            break
        if attempt < max_retries - 1:
            time.sleep(0.1)

    return response