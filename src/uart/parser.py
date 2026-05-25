import struct

def raw_bytes_to_int(data: bytes) -> int:
    return struct.unpack('<i', data)[0]

def raw_bytes_to_float(data: bytes) -> float:
    return struct.unpack('<f', data)[0]

def raw_bytes_to_string(data: bytes) -> str:
    return data.decode('ascii')

def int_to_raw_bytes(value: int) -> bytes:
    return struct.pack('<i', value)

def float_to_raw_bytes(value: float) -> bytes:
    return struct.pack('<f', value)

def string_to_raw_bytes(value: str) -> bytes:
    return value.encode('ascii')