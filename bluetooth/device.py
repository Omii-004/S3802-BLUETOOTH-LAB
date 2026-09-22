"""
bluetooth/device.py
===================
High-level device abstraction for the Samsung GT-S3802.
Manages socket lifecycle, connection state, and standard Bluetooth profile UUIDs.
"""

from enum import Enum, auto
import socket
from typing import Optional

from bluetooth.winsock import connect_winsock_rfcomm


class ConnectionState(Enum):
    """Bluetooth device connection state."""
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()


class S3802Device:
    """High-level Bluetooth manager for Samsung GT-S3802 feature phone."""

    SERVICES = {
        "opp": "00001105-0000-1000-8000-00805F9B34FB",   # Object Push Profile
        "ftp": "00001106-0000-1000-8000-00805F9B34FB",   # OBEX File Transfer
        "pbap": "0000112F-0000-1000-8000-00805F9B34FB",  # Phonebook Access
        "spp": "00001101-0000-1000-8000-00805F9B34FB",   # Serial Port Profile
    }

    def __init__(self, mac_address: str = "64:B3:10:24:36:66"):
        self.mac_address = mac_address
        self.sock: Optional[socket.socket] = None
        self.state = ConnectionState.DISCONNECTED
        self.active_service: Optional[str] = None

    @property
    def is_connected(self) -> bool:
        return self.state == ConnectionState.CONNECTED and self.sock is not None

    def connect(self, service: str = "opp") -> bool:
        """Connect to phone using service alias ('opp', 'ftp', etc.) or explicit UUID."""
        uuid_str = self.SERVICES.get(service.lower(), service)
        self.state = ConnectionState.CONNECTING

        sock, error_code = connect_winsock_rfcomm(self.mac_address, uuid_str)
        if error_code != 0:
            self.state = ConnectionState.DISCONNECTED
            raise ConnectionError(
                f"Failed to connect to S3802 ({self.mac_address}) "
                f"on service '{service}' (Winsock error: {error_code})"
            )

        self.sock = sock
        self.state = ConnectionState.CONNECTED
        self.active_service = service
        return True

    def disconnect(self) -> None:
        """Close active Bluetooth RFCOMM socket cleanly."""
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except OSError:
                pass
            finally:
                self.sock = None

        self.state = ConnectionState.DISCONNECTED
        self.active_service = None

    def send_bytes(self, data: bytes) -> int:
        """Send raw binary data over connected RFCOMM socket."""
        if not self.is_connected or self.sock is None:
            raise RuntimeError("Device is not connected.")
        return self.sock.send(data)

    def recv_bytes(self, max_bytes: int = 4096) -> bytes:
        """Receive binary data from connected RFCOMM socket."""
        if not self.is_connected or self.sock is None:
            raise RuntimeError("Device is not connected.")
        return self.sock.recv(max_bytes)