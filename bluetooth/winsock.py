"""
bluetooth/winsock.py
====================
Windows-native Bluetooth Winsock (ws2_32.dll) FFI bindings using ctypes.
Provides AF_BTH socket structures and RFCOMM UUID connection helpers.
"""

import ctypes
from ctypes import wintypes
import socket
from typing import Tuple

# Windows Winsock DLL Interface
ws2_32 = ctypes.windll.ws2_32

# Winsock Bluetooth Constants
AF_BTH = 32
SOCK_STREAM = 1
BTHPROTO_RFCOMM = 3


class GUID(ctypes.Structure):
    """128-bit GUID structure matching Win32 GUID layout."""
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8),
    ]


class SOCKADDR_BTH(ctypes.Structure):
    """Bluetooth socket address structure (SOCKADDR_BTH)."""
    _pack_ = 1
    _fields_ = [
        ("addressFamily", ctypes.c_ushort),
        ("btAddr", ctypes.c_ulonglong),
        ("serviceClassId", GUID),
        ("port", wintypes.ULONG),
    ]


# Bind ws2_32.connect arguments and return type
ws2_32.connect.argtypes = [
    ctypes.c_size_t,
    ctypes.POINTER(SOCKADDR_BTH),
    ctypes.c_int,
]
ws2_32.connect.restype = ctypes.c_int


def mac_to_bth_addr(mac_address: str) -> int:
    """Convert standard MAC string ('64:B3:10:24:36:66') to 48-bit unsigned integer."""
    clean_mac = mac_address.replace(":", "").replace("-", "").strip()
    return int(clean_mac, 16)


def uuid_to_guid(uuid_str: str) -> GUID:
    """Convert standard 36-char UUID string to Win32 GUID structure."""
    clean_uuid = uuid_str.replace("-", "").strip()
    if len(clean_uuid) != 32:
        raise ValueError(f"Invalid UUID length: {uuid_str}")

    data1 = int(clean_uuid[0:8], 16)
    data2 = int(clean_uuid[8:12], 16)
    data3 = int(clean_uuid[12:16], 16)

    data4_bytes = (wintypes.BYTE * 8)(
        *(int(clean_uuid[i : i + 2], 16) for i in range(16, 32, 2))
    )

    return GUID(data1, data2, data3, data4_bytes)


def connect_winsock_rfcomm(
    mac_address: str, service_uuid_str: str
) -> Tuple[socket.socket, int]:
    """
    Creates an AF_BTH socket and connects to a Bluetooth device using service UUID.
    Windows resolves the RFCOMM channel dynamically (SDP) when port=0.

    Returns:
        Tuple[socket.socket, int]: (connected Python socket, status code)
    """
    sock = socket.socket(AF_BTH, SOCK_STREAM, BTHPROTO_RFCOMM)
    sock.setblocking(True)

    sockaddr = SOCKADDR_BTH()
    sockaddr.addressFamily = AF_BTH
    sockaddr.btAddr = mac_to_bth_addr(mac_address)
    sockaddr.serviceClassId = uuid_to_guid(service_uuid_str)
    sockaddr.port = 0  # Dynamic SDP port resolution

    result = ws2_32.connect(
        sock.fileno(),
        ctypes.byref(sockaddr),
        ctypes.sizeof(sockaddr),
    )

    if result != 0:
        error_code = ws2_32.WSAGetLastError()
        sock.close()
        return None, error_code

    return sock, 0