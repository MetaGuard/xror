import typing
import struct

def decode_int(fa: typing.BinaryIO) -> int:
    bytes = fa.read(4)
    return int.from_bytes(bytes, 'little')

def decode_long(fa: typing.BinaryIO) -> int:
    bytes = fa.read(8)
    return int.from_bytes(bytes, 'little')

def decode_byte(fa: typing.BinaryIO) -> int:
    bytes = fa.read(1)
    return int.from_bytes(bytes, 'little')

def decode_bool(fa: typing.BinaryIO) -> bool:
    return 1 == decode_byte(fa)

def decode_string(fa: typing.BinaryIO) -> str:
    length = decode_int(fa)
    if length == 0:
        return ''
    result = fa.read(length)
    result = result.decode("utf-8")
    return result

# thanks https://github.com/Metalit/Replay/commit/3d63185c7a5863c1e3964e8e228f2d9dd8769168
def decode_string_maybe_utf16(fa: typing.BinaryIO) -> str:
    length = decode_int(fa)
    if length == 0:
        return ''
    result = list(fa.read(length))

    next_string_len= decode_int(fa)
    while next_string_len < 0 or next_string_len > 100:
        fa.seek(-4, 1)
        result.append(decode_byte(fa))
        next_string_len= decode_int(fa)
    fa.seek(-4, 1)

    result = bytes(result).decode("utf-8")
    return result


def decode_float(fa: typing.BinaryIO) -> float:
    bytes = fa.read(4)
    try:
        result = struct.unpack('f', bytes)
    except:
        raise;
    return result[0]
