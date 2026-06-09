MATRICULA = bytes([0, 2, 9, 5, 1, 2])

LPR1 = b'\x11'
LPR2 = b'\x12'
LPR3 = b'\x13'
LPR4 = b'\x14'

STATE = b'\x20'

READ = b'\x03'
WRITE = b'\x10'

MODBUS_ERRORS = { # https://docs.aveva.com/bundle/sp-cdp-drivers/page/192126.html
    0x01: 'ILLEGAL FUNCTION',
    0x02: 'ILLEGAL DATA ADDRESS',
    0x03: 'ILLEGAL DATA VALUE',
    0x04: 'ILLEGAL RESPONSE LENGTH',
    0x05: 'ACKNOWLEDGE',
    0x06: 'SLAVE DEVICE BUSY',
    0x07: 'NEGATIVE ACKNOWLEDGE',
    0x08: 'MEMORY PARITY ERROR',
    0x0A: 'GATEWAY PATH UNAVAILABLE',
    0x0B: 'GATEWAY TARGET DEVICE FAILED TO RESPOND'
}

def get_camera_from_sensor(sensor):
    return{
            'sensor_1': LPR1,
            'sensor_2': LPR2,
            'sensor_3': LPR3,
            'sensor_4': LPR4
        }[sensor]

def get_sensor_from_camera(camera):
    return{
            LPR1: 'sensor_1',
            LPR2: 'sensor_2',
            LPR3: 'sensor_3',
            LPR4: 'sensor_4'
        }[camera]