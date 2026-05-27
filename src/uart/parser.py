import struct

def bytes_to_int(data: bytes) -> int:
    return struct.unpack('<i', data)[0]

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