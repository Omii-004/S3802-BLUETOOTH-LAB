"""
obex/connect.py
===============
OBEX CONNECT session handshake implementation.
Negotiates OBEX protocol version and maximum packet payload size with S3802.
"""

import struct
from typing import Tuple

from bluetooth.device import S3802Device
from obex.packet import build_packet, parse_response, OPCODE_CONNECT


def obex_connect(
    device: S3802Device, proposed_max_len: int = 8192
) -> Tuple[bool, int]:
    """
    Perform OBEX CONNECT handshake.
    
    Payload Structure:
        [1 Byte: Version (0x10)] [1 Byte: Flags (0x00)] [2 Bytes: Max Length]

    Returns:
        Tuple[bool, int]: (success_status, negotiated_max_packet_len)
    """
    if not device.is_connected:
        raise RuntimeError("Device socket is not connected.")

    # Build CONNECT body: OBEX v1.0 (0x10), Flags 0x00, Proposed MTU
    connect_data = bytes([0x10, 0x00]) + struct.pack(">H", proposed_max_len)
    connect_pkt = build_packet(OPCODE_CONNECT, connect_data)

    device.send_bytes(connect_pkt)
    rx_bytes = device.recv_bytes(4096)
    response = parse_response(rx_bytes)

    if not response.is_success:
        return False, 0

    # Parse response payload: [1B Version] [1B Flags] [2B Negotiated Max Length]
    if len(response.payload) >= 4:
        negotiated_len = struct.unpack(">H", response.payload[2:4])[0]
    else:
        negotiated_len = proposed_max_len

    return True, negotiated_len