import ctypes
from ctypes import wintypes
from multiprocessing import context

from django.db.models import query

# ============================================================
# Samsung S3802 - Bluetooth SDP query
# Specifically searches for OBEX File Transfer (0x1106)
# ============================================================

ws2 = ctypes.WinDLL(
    "Ws2_32.dll",
    use_last_error=True
)

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

NS_BTH = 16

LUP_RETURN_NAME = 0x00000010
LUP_RETURN_ADDR = 0x00000100
LUP_RETURN_BLOB = 0x00000200
LUP_FLUSHCACHE = 0x00001000

AF_BTH = 32


# ------------------------------------------------------------
# GUID
# ------------------------------------------------------------

class GUID(ctypes.Structure):

    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


# ------------------------------------------------------------
# BLOB
# ------------------------------------------------------------

class BLOB(ctypes.Structure):

    _fields_ = [
        ("cbSize", wintypes.ULONG),
        (
            "pBlobData",
            ctypes.POINTER(ctypes.c_ubyte)
        ),
    ]


# ------------------------------------------------------------
# WSAQUERYSETW
# ------------------------------------------------------------

class WSAQUERYSETW(ctypes.Structure):

    _fields_ = [
        ("dwSize", wintypes.DWORD),
        (
            "lpszServiceInstanceName",
            wintypes.LPWSTR
        ),
        (
            "lpServiceClassId",
            ctypes.POINTER(GUID)
        ),
        ("lpVersion", ctypes.c_void_p),
        ("lpszComment", wintypes.LPWSTR),
        ("dwNameSpace", wintypes.DWORD),
        (
            "lpNSProviderId",
            ctypes.POINTER(GUID)
        ),
        ("lpszContext", wintypes.LPWSTR),
        ("dwNumberOfProtocols", wintypes.DWORD),
        ("lpafpProtocols", ctypes.c_void_p),
        ("lpszQueryString", wintypes.LPWSTR),
        ("dwNumberOfCsAddrs", wintypes.DWORD),
        ("lpcsaBuffer", ctypes.c_void_p),
        ("dwOutputFlags", wintypes.DWORD),
        (
            "lpBlob",
            ctypes.POINTER(BLOB)
        ),
    ]


# ------------------------------------------------------------
# Winsock
# ------------------------------------------------------------

class WSADATA(ctypes.Structure):

    _fields_ = [
        ("wVersion", wintypes.WORD),
        ("wHighVersion", wintypes.WORD),
        ("szDescription", ctypes.c_char * 257),
        ("szSystemStatus", ctypes.c_char * 129),
        ("iMaxSockets", wintypes.WORD),
        ("iMaxUdpDg", wintypes.WORD),
        ("lpVendorInfo", ctypes.c_char_p),
    ]


ws2.WSAStartup.argtypes = [
    wintypes.WORD,
    ctypes.POINTER(WSADATA)
]

ws2.WSAStartup.restype = ctypes.c_int


ws2.WSACleanup.argtypes = []

ws2.WSACleanup.restype = ctypes.c_int


ws2.WSALookupServiceBeginW.argtypes = [
    ctypes.POINTER(WSAQUERYSETW),
    wintypes.DWORD,
    ctypes.POINTER(wintypes.HANDLE),
]

ws2.WSALookupServiceBeginW.restype = ctypes.c_int


ws2.WSALookupServiceNextW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    ctypes.c_void_p,
]

ws2.WSALookupServiceNextW.restype = ctypes.c_int


ws2.WSALookupServiceEnd.argtypes = [
    wintypes.HANDLE
]

ws2.WSALookupServiceEnd.restype = ctypes.c_int


# ============================================================
# Helper: create GUID
# ============================================================

def make_guid():

    # 00001106-0000-1000-8000-00805F9B34FB
    # OBEX File Transfer

    g = GUID()

    g.Data1 = 0x00001106
    g.Data2 = 0x0000
    g.Data3 = 0x1000

    values = [
        0x80,
        0x00,
        0x00,
        0x80,
        0x5F,
        0x9B,
        0x34,
        0xFB
    ]

    for i, value in enumerate(values):

        g.Data4[i] = value

    return g


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print("Samsung S3802 - OBEX SDP Query")
    print("=" * 70)

    phone_address = "64B310243666"

    print("\nTarget Bluetooth address:")
    print(phone_address)

    print("\nTarget service:")
    print("OBEX File Transfer")
    print("UUID: 00001106-0000-1000-8000-00805F9B34FB")

    # --------------------------------------------------------
    # WSAStartup
    # --------------------------------------------------------

    wsa = WSADATA()

    result = ws2.WSAStartup(
        0x0202,
        ctypes.byref(wsa)
    )

    if result != 0:

        print("\nWSAStartup failed:", result)
        return

    print("\nWinsock initialized.")

    handle = wintypes.HANDLE()

    try:

        # ----------------------------------------------------
        # Build Bluetooth query
        # ----------------------------------------------------

        query = WSAQUERYSETW()

        query.dwSize = ctypes.sizeof(
            WSAQUERYSETW
        )

        # Bluetooth namespace
        query.dwNameSpace = NS_BTH

        # Specific service UUID
        service_guid = make_guid()

        query.lpServiceClassId = ctypes.pointer(
            service_guid
        )

        # Target Bluetooth device
        context = ctypes.create_unicode_buffer(phone_address)

        query.lpszContext = ctypes.cast(
            context,
            wintypes.LPWSTR
        )

        # Required to be zero
        query.dwNumberOfCsAddrs = 0

        # ----------------------------------------------------
        # Start SDP lookup
        # ----------------------------------------------------

        flags = (
            LUP_RETURN_NAME |
            LUP_RETURN_ADDR |
            LUP_RETURN_BLOB |
            LUP_FLUSHCACHE
        )

        print(
            "\nQuerying S3802 SDP..."
        )

        result = ws2.WSALookupServiceBeginW(
            ctypes.byref(query),
            flags,
            ctypes.byref(handle)
        )

        if result != 0:

            error = ctypes.get_last_error()

            print(
                "\nWSALookupServiceBeginW FAILED"
            )

            print("Return:", result)
            print("Error:", error)

            try:
                print(
                    "Message:",
                    ctypes.WinError(error)
                )
            except:
                pass

            return

        print(
            "\nSDP query started successfully!"
        )

        # ----------------------------------------------------
        # Get results
        # ----------------------------------------------------

        count = 0

        while True:

            buffer_size = 65536

            buffer = ctypes.create_string_buffer(
                buffer_size
            )

            size = wintypes.DWORD(
                buffer_size
            )

            result = ws2.WSALookupServiceNextW(
                handle,
                0,
                ctypes.byref(size),
                buffer
            )

            if result != 0:

                error = ctypes.get_last_error()

                print(
                    "\nLookup finished."
                )

                print(
                    "Last error:",
                    error
                )

                if error == 10108:

                    print(
                        "No matching service was found."
                    )

                break

            count += 1

            service = ctypes.cast(
                buffer,
                ctypes.POINTER(
                    WSAQUERYSETW
                )
            ).contents

            print("\n" + "=" * 70)

            if service.lpszServiceInstanceName:

                print(
                    "SERVICE:",
                    service.lpszServiceInstanceName
                )

            else:

                print(
                    "SERVICE: <unnamed>"
                )

            print(
                "Address count:",
                service.dwNumberOfCsAddrs
            )

            # ------------------------------------------------
            # SDP record
            # ------------------------------------------------

            if service.lpBlob:

                blob = service.lpBlob.contents

                print(
                    "SDP blob size:",
                    blob.cbSize
                )

                if (
                    blob.cbSize > 0
                    and blob.pBlobData
                ):

                    data = ctypes.string_at(
                        blob.pBlobData,
                        blob.cbSize
                    )

                    print(
                        "\nSDP RECORD HEX:"
                    )

                    print(
                        data.hex(" ")
                    )

        print(
            "\nMatching records:",
            count
        )

    finally:

        if handle:

            ws2.WSALookupServiceEnd(
                handle
            )

        ws2.WSACleanup()

        print(
            "\nWinsock cleaned up."
        )


if __name__ == "__main__":

    main()