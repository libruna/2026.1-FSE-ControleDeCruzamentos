import struct
import re

def bytes_to_int(data: bytes, le = False) -> int:
    return struct.unpack('<i' if not le else '>i', data)[0]

def bytes_to_float(data: bytes) -> float:
    return struct.unpack('<f', data)[0]

def bytes_to_string(data: bytes) -> str:
    return data.decode('ascii')

def int_to_bytes(value: int) -> bytes:
    return struct.pack('<i', value)

def float_to_bytes(value: float) -> bytes:
    return struct.pack('<f', value)

def string_to_bytes(value: str) -> bytes:
    return value.encode('ascii')

def raw_bytes_to_int(bytes):
    res = 0
    for i in range(len(bytes)):
        res += bytes[len(bytes) - 1 - i] * 10**i
    return res

def strhex(s):
    return "b'" + re.sub(r'.', lambda m: f'\\x{ord(m.group(0)):02x}', s.decode('latin1')) + "'"