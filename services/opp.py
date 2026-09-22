"""
services/opp.py
===============
Object Push Profile (OPP UUID 0x1105) service implementation.
Provides simple API for pushing and pulling text notes, JPEGs, and raw files on S3802.
"""

from typing import Callable, Optional, Tuple

from bluetooth.device import S3802Device
from obex.connect import obex_connect
from obex.get import obex_get_object
from obex.put import obex_put_file


class ObjectPushService:
    """Object Push Profile (OPP) client for Samsung GT-S3802."""

    def __init__(self, device: S3802Device):
        self.device = device
        self.max_packet_len = 8192

    def connect(self) -> bool:
        """Connect to OPP service (0x1105) and perform OBEX CONNECT handshake."""
        if not self.device.is_connected:
            self.device.connect(service="opp")

        success, mtu = obex_connect(self.device)
        if success:
            self.max_packet_len = mtu
        return success

    def push_file(
        self,
        filename: str,
        file_bytes: bytes,
        mime_type: str = "text/plain",
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> bool:
        """Push a file object to the phone."""
        return obex_put_file(
            device=self.device,
            filename=filename,
            file_bytes=file_bytes,
            mime_type=mime_type,
            max_packet_len=self.max_packet_len,
            progress_callback=progress_callback,
        )

    def push_text(self, filename: str, text: str) -> bool:
        """Push a text file note to the phone."""
        if not filename.endswith(".txt"):
            filename += ".txt"
        text_bytes = text.encode("utf-8")
        return self.push_file(filename, text_bytes, mime_type="text/plain")

    def push_image(self, filename: str, image_bytes: bytes) -> bool:
        """Push a JPEG image to the phone."""
        return self.push_file(filename, image_bytes, mime_type="image/jpeg")

    def pull_file(self, filename: str, mime_type: Optional[str] = None) -> Tuple[bool, bytes]:
        """Pull/get an object from the phone via OBEX GET."""
        return obex_get_object(self.device, filename, mime_type=mime_type)