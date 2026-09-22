"""
obex/get.py
===========
OBEX GET request handler per IrDA OBEX 1.0 specification.
Retrieves objects/files from the Samsung GT-S3802 over RFCOMM.
"""

from typing import Optional, Tuple

from bluetooth.device import S3802Device
from obex.headers import encode_name, encode_type, parse_headers, HEADER_BODY, HEADER_END_OF_BODY
from obex.packet import (
    build_packet,
    parse_response,
    OPCODE_GET_FINAL,
    RESPONSE_CONTINUE,
    RESPONSE_SUCCESS,
)


def obex_get_object(
    device: S3802Device,
    object_name: str,
    mime_type: Optional[str] = None,
) -> Tuple[bool, bytes]:
    """
    Issue an OBEX GET request to retrieve an object from the S3802 device.

    Args:
        device (S3802Device): Connected S3802 Bluetooth device instance.
        object_name (str): Name of the target file/object to retrieve.
        mime_type (Optional[str]): Optional MIME type (e.g., 'text/x-vcard').

    Returns:
        Tuple[bool, bytes]: (success_flag, retrieved_binary_payload)
    """
    if not device.is_connected:
        raise RuntimeError("Device socket is not connected.")

    # Build initial GET headers (Name + optional Type)
    headers_payload = encode_name(object_name)
    if mime_type:
        headers_payload += encode_type(mime_type)

    packet = build_packet(OPCODE_GET_FINAL, headers_payload)
    device.send_bytes(packet)

    accumulated_data = bytearray()

    while True:
        rx_bytes = device.recv_bytes(8192)
        response = parse_response(rx_bytes)

        # Parse headers in response to extract BODY (0x48) or END_OF_BODY (0x49)
        parsed_hdrs = parse_headers(response.payload)

        if HEADER_BODY in parsed_hdrs:
            accumulated_data.extend(parsed_hdrs[HEADER_BODY])
        if HEADER_END_OF_BODY in parsed_hdrs:
            accumulated_data.extend(parsed_hdrs[HEADER_END_OF_BODY])

        if response.is_success:
            return True, bytes(accumulated_data)
        elif response.is_continue:
            # Request next payload chunk using empty GET request
            next_pkt = build_packet(OPCODE_GET_FINAL, b"")
            device.send_bytes(next_pkt)
        else:
            # Transfer failed or rejected (e.g. 0xC4 Not Found)
            return False, bytes(accumulated_data)