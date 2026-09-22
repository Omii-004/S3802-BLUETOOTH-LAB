"""
obex/put.py
===========
OBEX PUT file transfer engine with chunking and '0x90 Continue' handling.
Transfers text, image, and data files to the Samsung S3802.
"""

from typing import Callable, Optional

from bluetooth.device import S3802Device
from obex.headers import encode_body, encode_length, encode_name, encode_type
from obex.packet import (
    build_packet,
    parse_response,
    OPCODE_PUT,
    OPCODE_PUT_FINAL,
    RESPONSE_CONTINUE,
    RESPONSE_SUCCESS,
)


def obex_put_file(
    device: S3802Device,
    filename: str,
    file_bytes: bytes,
    mime_type: str = "text/plain",
    max_packet_len: int = 8192,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> bool:
    """
    Upload a file object to the Samsung GT-S3802 via OBEX PUT.
    Supports payload chunking if file size exceeds MTU.
    """
    if not device.is_connected:
        raise RuntimeError("Device is not connected.")

    headers_bytes = encode_name(filename) + encode_type(mime_type) + encode_length(len(file_bytes))
    
    # Calculate chunk size (reserved 16 bytes for body header overhead)
    chunk_size = max(512, max_packet_len - len(headers_bytes) - 32)
    offset = 0
    total_bytes = len(file_bytes)

    while offset < total_bytes or total_bytes == 0:
        chunk = file_bytes[offset : offset + chunk_size]
        offset += len(chunk)
        is_final = (offset >= total_bytes)

        body_header = encode_body(chunk, is_final=is_final)
        opcode = OPCODE_PUT_FINAL if is_final else OPCODE_PUT

        if offset <= len(chunk):
            payload = headers_bytes + body_header
        else:
            payload = body_header

        packet = build_packet(opcode, payload)
        device.send_bytes(packet)

        rx_bytes = device.recv_bytes(4096)
        response = parse_response(rx_bytes)

        if progress_callback:
            progress_callback(min(offset, total_bytes), total_bytes)

        if is_final:
            return response.is_success
        elif response.code != RESPONSE_CONTINUE:
            raise IOError(f"OBEX PUT rejected by device with code: 0x{response.code:02X}")

    return True