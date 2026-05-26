def calculate_crc(data: bytes) -> bytes:
    crc = 0
    for byte in data:
        crc ^= byte

        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1

    return crc.to_bytes(2, byteorder='little')