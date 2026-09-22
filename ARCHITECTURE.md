# S3802-Bluetooth-Lab: System & Protocol Architecture

## 1. System Philosophy & Objectives
The goal of `S3802-Bluetooth-Lab` is to interface a modern Windows PC with a legacy Samsung GT-S3802 feature phone over Bluetooth RFCOMM and OBEX protocols. The architecture is engineered around three non-negotiable principles:
1. **100% Offline / Air-Gapped**: Zero external cloud services, internet dependencies, or external telemetry.
2. **Native Windows Transport**: Bypassing dead or broken third-party wrappers (such as `PyBluez` which fails under Python 3.12+ due to the deprecation of `2to3`) by directly consuming Microsoft Winsock via Python's standard `ctypes` and `socket` modules.
3. **Decoupled Layering**: Protocol encoding/decoding is pure, stateless byte manipulation—completely isolated from physical socket I/O. This guarantees that all protocol logic can be unit-tested without a physical phone present.

---

## 2. Multi-Layer System Architecture

```
+=============================================================================+
|                           LAYER 4: APPLICATION & GUI                        |
|                                                                             |
|   +---------------------------------------------------------------------+   |
|   |                    Tkinter Desktop Controller                       |   |
|   |   - Device Scanner & Pairing Manager   - Real-Time Hex Stream Log   |   |
|   |   - Canvas Image Composer (Pillow)     - File Transfer Center       |   |
|   +---------------------------------------------------------------------+   |
+======================================+======================================+
                                       | Events / Queues / Worker Threads
+======================================v======================================+
|                          LAYER 3: SERVICE PROFILES                          |
|                                                                             |
|   +-------------------+  +-------------------+  +-----------------------+   |
|   |  services.opp     |  |  services.ftp     |  |  services.pbap        |   |
|   |  - Object Push    |  |  - File Transfer  |  |  - Phonebook Access   |   |
|   |  - Single PUT/GET |  |  - Directory List |  |  - vCard Extraction  |   |
|   +---------+---------+  +---------+---------+  +-----------+-----------+   |
+=============|======================|========================|===============+
              +----------------------+------------------------+
                                     | OBEX Operations (CONNECT, PUT, GET)
+====================================v========================================+
|                       LAYER 2: PROTOCOL ENGINE (OBEX)                       |
|                                                                             |
|   +--------------------------+  +---------------------------------------+   |
|   |       obex.packet        |  |             obex.headers              |   |
|   |   - Opcode serialization |  |   - 0x01: Name (UTF-16BE null-term)   |   |
|   |   - Response code parse  |  |   - 0x42: Type (ASCII null-term)      |   |
|   |   - Packet length header |  |   - 0xC3: Length (32-bit uint)        |   |
|   |   - Chunking & Reassembly|  |   - 0x48: Body / 0x49: End-of-Body    |   |
|   +--------------------------+  +---------------------------------------+   |
+======================================+======================================+
                                       | Pure byte buffers (TX / RX)
+======================================v======================================+
|                       LAYER 1: TRANSPORT (BLUETOOTH)                        |
|                                                                             |
|   +---------------------------------------------------------------------+   |
|   |                           bluetooth.device                          |   |
|   |   - S3802 Device Abstraction & Connection Lifecycle Manager         |   |
|   +----------------------------------+----------------------------------+   |
|                                      |                                      |
|   +----------------------------------v----------------------------------+   |
|   |                          bluetooth.winsock                          |   |
|   |   - AF_BTH (32), BTHPROTO_RFCOMM (3)                                |   |
|   |   - ctypes bindings: ws2_32.connect, WSAGetLastError                |   |
|   |   - Structures: GUID, SOCKADDR_BTH                                  |   |
|   |   - Dynamic SDP Service UUID Resolution (port = 0)                  |   |
|   +---------------------------------------------------------------------+   |
+======================================+======================================+
                                       | Physical RFCOMM Channel over 2.4 GHz
+======================================v======================================+
|                   HARDWARE ENDPOINT: SAMSUNG GT-S3802                       |
|   MAC: 64:B3:10:24:36:66                                                    |
|   Services: OPP (0x1105) [Proven], FTP (0x1106), PBAP (0x112F), SPP (COM5) |
+=============================================================================+
```

---

## 3. Detailed Component Responsibilities

### Layer 1: Transport Layer (`bluetooth/`)
- **`bluetooth/winsock.py`**:
  - Direct Win32 / Winsock2 foreign function interface (`ws2_32.dll`).
  - Defines the C-compatible data structures:
    - `GUID`: 128-bit Universally Unique Identifier used by Bluetooth SDP.
    - `SOCKADDR_BTH`: Bluetooth socket address struct containing `addressFamily`, `btAddr` (48-bit unsigned integer), `serviceClassId` (`GUID`), and `port` (RFCOMM channel number).
  - Implements dynamic service-to-channel resolution: setting `port = 0` and assigning `serviceClassId` signals the Windows Bluetooth subsystem to perform an SDP query automatically, avoiding brittle hardcoded RFCOMM channels.
- **`bluetooth/device.py`**:
  - Provides the high-level `S3802` class.
  - Manages socket instantiation, connect timeouts, state transitions (`DISCONNECTED`, `CONNECTING`, `CONNECTED`), and clean socket termination.

### Layer 2: Protocol Engine (`obex/`)
- **`obex/headers.py`**:
  - Implements serialization and deserialization for OBEX header IDs per the IrDA/OBEX 1.0 specification:
    - `0x01` (`NAME`): UTF-16BE encoded unicode string with 2-byte null terminator.
    - `0x42` (`TYPE`): ASCII MIME type string with null terminator (e.g., `"image/jpeg\x00"`).
    - `0xC3` (`LENGTH`): 4-byte big-endian unsigned integer representing total payload size.
    - `0x48` (`BODY`): Intermediate data chunk.
    - `0x49` (`END_OF_BODY`): Final chunk terminating an object stream.
- **`obex/packet.py`**:
  - Packets adhere to the standard IrDA OBEX layout:
    - Byte 0: `Opcode` (e.g., `0x80` CONNECT, `0x02` PUT continue, `0x82` PUT final, `0x03` GET continue, `0x83` GET final). The high bit (`0x80`) is the `Final` flag.
    - Bytes 1-2: `Packet Length` (16-bit big-endian unsigned integer representing total packet size including opcode and length header).
    - Bytes 3+: Optional protocol headers and payload.
  - Parses response codes: `0xA0` (Success), `0x90` (Continue), `0xC0` (Bad Request), `0xC4` (Not Found).
- **`obex/connect.py`**:
  - Builds the OBEX CONNECT payload (Opcode `0x80`, OBEX version `0x10`, Flags `0x00`, Max Packet Length `0x2000` = 8192 bytes).
  - Unpacks the receiver's negotiated packet size (e.g., `0xFC00` = 64,512 bytes on the S3802).
- **`obex/put.py`**:
  - Manages stream fragmentation (chunking) when pushing files larger than the negotiated maximum packet size, handling intermediate `0x90 Continue` acknowledgments.

### Layer 3: Service Profiles (`services/`)
- **`services/opp.py`**: Object Push Profile (UUID `00001105-0000-1000-8000-00805F9B34FB`). Provides atomic push operations for standalone objects (JPEGs, vCards).
- **`services/ftp.py`**: OBEX File Transfer Profile (UUID `00001106-0000-1000-8000-00805F9B34FB`). Handles multi-folder browsing and hierarchical navigation.
- **`services/pbap.py`**: Phonebook Access Profile (UUID `0000112F-0000-1000-8000-00805F9B34FB`). Specialized OBEX GET commands targeting virtual vCard folders.

---

## 4. Error Handling & Network Resilience
1. **Winsock Error Translation**:
   - `10049` (`WSAEADDRNOTAVAIL`): Invalid MAC address formatting or unmapped service GUID.
   - `10051` (`WSAENETUNREACH`): Bluetooth adapter disabled or phone out of range.
   - `10054` (`WSAECONNRESET`): Phone dropped connection (e.g., user pressed Cancel or screen timed out).
   - `10060` (`WSAETIMEDOUT`): SDP query or RFCOMM link establishment timed out.
2. **Buffer Safety**:
   - Outgoing packets are strictly limited to `negotiated_max_packet_len - 3` to avoid buffer overflows on the phone's baseband controller.
