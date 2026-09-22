"""
obex/packet.py
==============
Generic OBEX binary packet assembler, response decoder, and status code map.
Processes IrDA OBEX packet headers: [Opcode 1B] [Packet Length 2B] [Payload].
"""

import struct
from typing import NamedTuple, Tuple

# OBEX Request Opcodes (High Bit 0x80 indicates 'Final' packet)
OPCODE_CONNECT = 0x80
OPCODE_DISCONNECT = 0x81
OPCODE_PUT = 0x02
OPCODE_PUT_FINAL = 0x82
OPCODE_GET = 0x03
OPCODE_GET_FINAL = 0x83
OPCODE_SETPATH = 0x85
OPCODE_ABORT = 0xFF

# OBEX Response Codes
RESPONSE_SUCCESS = 0xA0       # 200 OK / Success
RESPONSE_CONTINUE = 0x90      # 100 Continue (Send next chunk)
RESPONSE_BAD_REQUEST = 0xC0   # 400 Bad Request
RESPONSE_UNAUTHORIZED = 0xC1  # 401 Unauthorized
RESPONSE_FORBIDDEN = 0xC3     # 403 Forbidden
RESPONSE_NOT_FOUND = 0xC4     # 404 Not Found
RESPONSE_NOT_ALLOWED = 0xC5   # 405 Method Not Allowed


class ObexResponse(NamedTuple):
    """Parsed OBEX Response Packet."""
    code: int
    length: int
    payload: bytes
    is_success: bool
    is_continue: bool


RESPONSE_NAMES = {
    RESPONSE_SUCCESS: "0xA0 Success (OK)",
    RESPONSE_CONTINUE: "0x90 Continue",
    RESPONSE_BAD_REQUEST: "0xC0 Bad Request",
    RESPONSE_UNAUTHORIZED: "0xC1 Unauthorized",
    RESPONSE_FORBIDDEN: "0xC3 Forbidden",
    RESPONSE_NOT_FOUND: "0xC4 Not Found",
    RESPONSE_NOT_ALLOWED: "0xC5 Method Not Allowed",
}


def build_packet(opcode: int, payload: bytes = b"") -> bytes:
    """
    Construct a complete OBEX request packet.
    Packet Structure:
        [1 Byte: Opcode] [2 Bytes: Total Packet Length (Big Endian)] [Payload Bytes]
    """
    total_len = 3 + len(payload)
    if total_len > 65535:
        raise ValueError(f"OBEX packet size exceeds 65535 bytes limit: {total_len}")

    return bytes([opcode]) + struct.pack(">H", total_len) + payload


def parse_response(data: bytes) -> ObexResponse:
    """
    Parse raw bytes received from RFCOMM socket into ObexResponse object.
    """
    if len(data) < 3:
        raise ValueError(f"OBEX response buffer underflow: received only {len(data)} bytes")

    code = data[0]
    total_len = struct.unpack(">H", data[1:3])[0]
    payload = data[3:total_len] if len(data) >= total_len else data[3:]

    is_success = (code == RESPONSE_SUCCESS)
    is_continue = (code == RESPONSE_CONTINUE)

    return ObexResponse(
        code=code,
        length=total_len,
        payload=payload,
        is_success=is_success,
        is_continue=is_continue,
    )


def get_response_description(code: int) -> str:
    """Return human-readable string for an OBEX status code."""
    return RESPONSE_NAMES.get(code, f"Unknown Code (0x{code:02X})")