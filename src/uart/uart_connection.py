import serial

def open_serial():
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
