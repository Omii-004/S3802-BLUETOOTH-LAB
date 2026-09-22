"""
obex/headers.py
===============
OBEX Header IDs and binary encoding/decoding functions per IrDA OBEX 1.0 spec.
Supports Name (UTF-16BE), Type (ASCII), Length (32-bit uint), and Body/End-of-Body chunks.
"""

import struct
from typing import Dict, Union

# Standard OBEX Header Identifiers
HEADER_NAME = 0x01         # Null-terminated UTF-16BE string (Unicode)
HEADER_TYPE = 0x42         # Null-terminated ASCII string (MIME type)
HEADER_LENGTH = 0xC3       # 4-byte 32-bit unsigned integer (Total length)
HEADER_TIME_ISO = 0x44     # ISO 8601 Timestamp
HEADER_BODY = 0x48         # Intermediate data chunk
HEADER_END_OF_BODY = 0x49  # Final data chunk terminating an object stream
HEADER_TARGET = 0x46       # Target UUID header
HEADER_WHO = 0x4A          # Who header
HEADER_CONNECTION_ID = 0xCB  # Connection ID header


def encode_name(filename: str) -> bytes:
    """
    Encode filename into OBEX Name Header (0x01).
    Format: [0x01] [2-byte Total Length] [UTF-16BE Bytes] [2-byte Null Terminator \x00\x00]
    """
    encoded_str = filename.encode("utf-16-be") + b"\x00\x00"
    header_len = 3 + len(encoded_str)
    return bytes([HEADER_NAME]) + struct.pack(">H", header_len) + encoded_str


def encode_type(mime_type: str) -> bytes:
    """
    Encode MIME type into OBEX Type Header (0x42).
    Format: [0x42] [2-byte Total Length] [ASCII Bytes] [1-byte Null Terminator \x00]
    """
    encoded_str = mime_type.encode("ascii") + b"\x00"
    header_len = 3 + len(encoded_str)
    return bytes([HEADER_TYPE]) + struct.pack(">H", header_len) + encoded_str


def encode_length(total_size: int) -> bytes:
    """
    Encode total file byte size into OBEX Length Header (0xC3).
    Format: [0xC3] [4-byte 32-bit Unsigned Integer Big-Endian]
    """
    return bytes([HEADER_LENGTH]) + struct.pack(">I", total_size)


def encode_body(chunk: bytes, is_final: bool = False) -> bytes:
    """
    Encode data chunk into OBEX Body (0x48) or End-of-Body (0x49) Header.
    Format: [0x48 or 0x49] [2-byte Total Length] [Raw Binary Payload]
    """
    header_id = HEADER_END_OF_BODY if is_final else HEADER_BODY
    header_len = 3 + len(chunk)
    return bytes([header_id]) + struct.pack(">H", header_len) + chunk


def parse_headers(data: bytes) -> Dict[int, Union[str, int, bytes]]:
    """Parse raw bytes stream and extract OBEX headers into a dictionary key-value pair."""
    headers = {}
    offset = 0
    data_len = len(data)

    while offset < data_len:
        hi = data[offset]
        encoding_prefix = hi & 0xC0

        if encoding_prefix == 0x00 or encoding_prefix == 0x40:
            # 2-byte length header (Unicode string or Byte sequence)
            if offset + 3 > data_len:
                break
            hlen = struct.unpack(">H", data[offset + 1 : offset + 3])[0]
            val = data[offset + 3 : offset + hlen]
            if hi == HEADER_NAME:
                headers[hi] = val[:-2].decode("utf-16-be", errors="ignore")
            elif hi == HEADER_TYPE:
                headers[hi] = val[:-1].decode("ascii", errors="ignore")
            else:
                headers[hi] = val
            offset += hlen

        elif encoding_prefix == 0xC0:
            # 4-byte 32-bit integer quantity
            if offset + 5 > data_len:
                break
            val = struct.unpack(">I", data[offset + 1 : offset + 5])[0]
            headers[hi] = val
            offset += 5

        elif encoding_prefix == 0x80:
            # 1-byte quantity
            if offset + 2 > data_len:
                break
            headers[hi] = data[offset + 1]
            offset += 2
        else:
            break

    return headers