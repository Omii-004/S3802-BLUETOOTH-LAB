import ctypes
from ctypes import wintypes
import socket
from pathlib import Path
import struct

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# Windows Winsock
# ============================================================

ws2_32 = ctypes.windll.ws2_32

AF_BTH = 32
SOCK_STREAM = 1
BTHPROTO_RFCOMM = 3


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8)
    ]


class SOCKADDR_BTH(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("addressFamily", ctypes.c_ushort),
        ("btAddr", ctypes.c_ulonglong),
        ("serviceClassId", GUID),
        ("port", wintypes.ULONG),
    ]


ws2_32.connect.argtypes = [
    ctypes.c_size_t,
    ctypes.POINTER(SOCKADDR_BTH),
    ctypes.c_int
]

ws2_32.connect.restype = ctypes.c_int


# ============================================================
# Phone
# ============================================================

PHONE_MAC = "64:B3:10:24:36:66"


def mac_to_bth_addr(mac):
    return int(
        mac.replace(":", "").replace("-", "").strip(),
        16
    )


# ============================================================
# OPP UUID 00001105-0000-1000-8000-00805F9B34FB
# ============================================================

opp_guid = GUID(
    0x00001105,
    0x0000,
    0x1000,
    (wintypes.BYTE * 8)(
        0x80, 0x00, 0x00, 0x80,
        0x5F, 0x9B, 0x34, 0xFB
    )
)


# ============================================================
# Create JPEG
# ============================================================

script_dir = Path(__file__).resolve().parent
image_path = script_dir / "test.jpg"

WIDTH = 800
HEIGHT = 480

image = Image.new("RGB", (WIDTH, HEIGHT), "white")
draw = ImageDraw.Draw(image)

try:
    font_large = ImageFont.truetype("arial.ttf", 55)
    font_medium = ImageFont.truetype("arial.ttf", 35)
except OSError:
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()


draw.text(
    (WIDTH // 2, 120),
    "HELLO FROM PYTHON",
    fill="black",
    font=font_large,
    anchor="mm"
)

draw.text(
    (WIDTH // 2, 230),
    "Samsung S3802",
    fill="black",
    font=font_medium,
    anchor="mm"
)

draw.text(
    (WIDTH // 2, 300),
    "Bluetooth OBEX Test",
    fill="black",
    font=font_medium,
    anchor="mm"
)

draw.text(
    (WIDTH // 2, 370),
    "NO INTERNET REQUIRED",
    fill="black",
    font=font_medium,
    anchor="mm"
)

image.save(image_path, "JPEG", quality=90)

file_data = image_path.read_bytes()

print("===================================================")
print(" Samsung S3802 - Python JPEG Bluetooth Test")
print("===================================================")
print()
print(f"Created: {image_path}")
print(f"JPEG size: {len(file_data)} bytes")
print()


# ============================================================
# Bluetooth socket address
# ============================================================

sockaddr = SOCKADDR_BTH()

sockaddr.addressFamily = AF_BTH
sockaddr.btAddr = mac_to_bth_addr(PHONE_MAC)
sockaddr.serviceClassId = opp_guid

# Let Windows resolve RFCOMM channel
sockaddr.port = 0


# ============================================================
# Connect
# ============================================================

print(
    f"Connecting to {PHONE_MAC} "
    f"on Object Push service 0x1105..."
)

s = socket.socket(
    AF_BTH,
    SOCK_STREAM,
    BTHPROTO_RFCOMM
)

s.setblocking(True)

res = ws2_32.connect(
    s.fileno(),
    ctypes.byref(sockaddr),
    ctypes.sizeof(sockaddr)
)

if res != 0:

    error_code = ws2_32.WSAGetLastError()

    print(
        f"[ERROR] Winsock connect failed: "
        f"{error_code}"
    )

    s.close()
    raise SystemExit(1)


print("[SUCCESS] Connected to S3802!")
print()


# ============================================================
# OBEX CONNECT
# ============================================================

obex_connect = bytes([
    0x80,
    0x00, 0x07,
    0x10,
    0x00,
    0x20, 0x00
])

print("Sending OBEX CONNECT...")

s.sendall(obex_connect)

s.settimeout(10)

response = s.recv(1024)

print(
    f"OBEX response: "
    f"{response.hex(' ')}"
)

if not response or response[0] != 0xA0:

    print("[ERROR] OBEX CONNECT failed.")

    s.close()
    raise SystemExit(1)


print("[SUCCESS] OBEX connection established!")
print()


# ============================================================
# OBEX helpers
# ============================================================

def unicode_header(header_id, text):

    encoded = (
        text.encode("utf-16-be")
        + b"\x00\x00"
    )

    length = 3 + len(encoded)

    return (
        bytes([header_id])
        + struct.pack(">H", length)
        + encoded
    )


def byte_sequence_header(header_id, data):

    length = 3 + len(data)

    return (
        bytes([header_id])
        + struct.pack(">H", length)
        + data
    )


def four_byte_header(header_id, value):

    return (
        bytes([header_id])
        + struct.pack(">I", value)
    )


# ============================================================
# Build OBEX PUT
# ============================================================

filename = "test.jpg"

name_header = unicode_header(
    0x01,
    filename
)

type_header = byte_sequence_header(
    0x42,
    b"image/jpeg\x00"
)

length_header = four_byte_header(
    0xC3,
    len(file_data)
)

body_header = byte_sequence_header(
    0x49,
    file_data
)

headers = (
    name_header
    + type_header
    + length_header
    + body_header
)

packet_length = 3 + len(headers)

obex_put = (
    bytes([0x82])
    + struct.pack(">H", packet_length)
    + headers
)


print("Preparing OBEX PUT...")
print(f"Filename: {filename}")
print(f"File size: {len(file_data)} bytes")
print(f"Packet size: {len(obex_put)} bytes")
print()

print("Sending JPEG to Samsung S3802...")

s.sendall(obex_put)

# ============================================================
# Response
# ============================================================

try:

    response = s.recv(1024)

    print()
    print(
        f"PUT response: "
        f"{response.hex(' ')}"
    )

    if response:

        code = response[0]

        if code == 0xA0:

            print()
            print("===================================================")
            print("[SUCCESS] JPEG TRANSFER ACCEPTED")
            print("===================================================")
            print()
            print("File:", filename)
            print()
            print("Now check the phone's Images/Gallery.")
            print("Open test.jpg to see the message.")

        elif code == 0x90:

            print()
            print("[INFO] Phone returned OBEX CONTINUE (0x90).")
            print("The file may require packet chunking.")

        else:

            print()
            print(
                f"[WARNING] Unexpected OBEX response: "
                f"0x{code:02X}"
            )

except socket.timeout:

    print("[TIMEOUT] No response from phone.")


# ============================================================
# OBEX DISCONNECT
# ============================================================

print()
print("Sending OBEX DISCONNECT...")

disconnect = bytes([
    0x81,
    0x00,
    0x03
])

try:

    s.sendall(disconnect)

    s.settimeout(3)

    response = s.recv(1024)

    if response:
        print(
            "Disconnect response:",
            response.hex(" ")
        )

except Exception as e:

    print(
        "Disconnect response not received:",
        e
    )


s.close()

print()
print("Bluetooth connection closed.")
print("Done.")