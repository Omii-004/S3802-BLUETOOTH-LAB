# 📱 S3802-Bluetooth-Lab & Desktop Controller

> **Controlling a legacy Samsung GT-S3802 feature phone from Python using native Windows Winsock APIs, RFCOMM transport, IrDA OBEX protocol engine, and a multi-threaded Tkinter desktop control suite.**

---

## 🌟 Executive Summary

**S3802-Bluetooth-Lab** is an offline, air-gapped systems research and desktop engineering project that transforms a legacy feature phone (Samsung GT-S3802) into a programmable Bluetooth peripheral and secondary display endpoint. 

By bypassing broken third-party libraries (such as `PyBluez` which fails under Python 3.12+ due to deprecated `2to3` setup hooks), this project implements a direct **Win32 Winsock (`ws2_32.dll`) foreign function interface** in Python. The system features a complete, stateless **IrDA OBEX 1.0 protocol engine** (CONNECT, PUT chunking, GET reassembly) and a full-featured **Tkinter Desktop Control Application**.

---

## 🚀 Key Features & Hardware Milestones

- **🔒 100% Offline & Air-Gapped**: Zero internet dependencies, cloud APIs, cellular data, or Wi-Fi requirements.
- **⚡ Native Windows Winsock Transport**: Built using Python standard library `ctypes` over Win32 `ws2_32.dll` (`AF_BTH = 32`, `BTHPROTO_RFCOMM = 3`).
- **🎯 Dynamic SDP Service UUID Resolution**: Passes 128-bit Bluetooth service GUIDs with `port=0` to allow the Windows Bluetooth stack to perform SDP channel discovery dynamically.
- **📦 Complete IrDA OBEX 1.0 Engine**: Decoupled binary header serializers (UTF-16BE `Name`, ASCII `Type`, 32-bit uint `Length`, `Body`/`End-of-Body` chunks) and packet framing.
- **🔄 Multi-Packet Chunking**: Handles large payloads with intermediate `0x90 Continue` acknowledgments up to the negotiated MTU (64,512 bytes on S3802).
- **📱 Hardware Proven**: Verified physical transmission of Pillow-rendered 800x480 JPEGs and plain text notes (`.txt`) directly opened on the Samsung GT-S3802 display.
- **🖥️ Multi-Threaded Desktop GUI**: Non-blocking `tkinter` desktop suite featuring:
  - **Connection Panel**: Dynamic LED status dot (Red/Orange/Green) and MTU readout.
  - **Image Studio**: Live on-screen Pillow canvas card generator & progress bar.
  - **Text Note Editor**: Multi-line note composer for sending plain text files.
  - **File Explorer**: System file picker dialog.
  - **Protocol Inspector**: Live syntax-highlighted hexadecimal stream monitor (`TX` in Blue, `RX` in Green, `ERR` in Red).

---

## 🏗️ System Architecture

```
+=============================================================================+
|                       LAYER 4: DESKTOP GUI APPLICATION                      |
|                                                                             |
|   +---------------------------------------------------------------------+   |
|   |                    Tkinter Desktop Controller                       |   |
|   |   - Connection Panel & LED Indicator  - Live Protocol Hex Inspector |   |
|   |   - Image Studio Canvas (Pillow)      - Text Note & File Pusher     |   |
|   +----------------------------------+----------------------------------+   |
+======================================|======================================+
                                       | Events / Queues / Worker Threads
+======================================v======================================+
|                          LAYER 3: SERVICE PROFILES                          |
|                                                                             |
|   +-------------------+  +-------------------+  +-----------------------+   |
|   |   services.opp    |  |   services.ftp    |  |   services.pbap       |   |
|   |   - Object Push   |  |   - File Transfer |  |   - Phonebook Access  |   |
|   |   - push_image()  |  |   - Directory List|  |   - vCard Extraction  |   |
|   |   - push_text()   |  |   - pull_file()   |  |                       |   |
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
                                       | Pure Byte Buffers (TX / RX)
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
                                       | Physical RFCOMM Link over 2.4 GHz
+======================================v======================================+
|                   HARDWARE ENDPOINT: SAMSUNG GT-S3802                       |
|   MAC: 64:B3:10:24:36:66                                                    |
|   Services: OPP (0x1105) [Proven], FTP (0x1106), PBAP (0x112F), SPP (COM5) |
+=============================================================================+
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.10+ | Core implementation & desktop application |
| **Transport** | Win32 Winsock (`ws2_32.dll`) | Native Windows Bluetooth socket binding via `ctypes` |
| **Protocol** | IrDA OBEX 1.0 / RFCOMM | Binary packet framing, header serialization & chunking |
| **GUI Framework** | Python `tkinter` & `ttk` | Multi-threaded desktop user interface |
| **Imaging Engine** | Pillow (`PIL`) | 800x480 JPEG card composition & live preview rendering |
| **Threading** | `threading` & `queue.Queue` | Non-blocking asynchronous background Bluetooth I/O |

---

## 📁 Repository Structure

```text
S3802-Bluetooth-Lab/
│
├── bluetooth/                  # Transport Layer (Winsock & Device)
│   ├── __init__.py
│   ├── winsock.py              # Win32 ws2_32.dll ctypes FFI & GUID/SOCKADDR_BTH
│   └── device.py               # S3802Device lifecycle & service UUID mapping
│
├── obex/                       # Protocol Engine Layer (IrDA OBEX 1.0)
│   ├── __init__.py
│   ├── headers.py              # UTF-16BE Name, ASCII Type, Length, Body encoders
│   ├── packet.py               # 3-byte packet framing & response decoder
│   ├── connect.py              # OBEX CONNECT handshake & MTU negotiation
│   ├── put.py                  # OBEX PUT file chunking engine (0x90 Continue)
│   └── get.py                  # OBEX GET request handler & object reassembly
│
├── services/                   # Service Profile Layer
│   ├── __init__.py
│   └── opp.py                  # Object Push Profile (0x1105) wrapper
│
├── gui/                        # Desktop GUI Application Layer
│   ├── __init__.py
│   ├── logger.py               # Thread-safe GuiLogger & LogEvent queue
│   ├── worker.py               # AsyncWorker daemon thread manager
│   ├── app.py                  # Main S3802App window assembly & queue polling
│   └── views/
│       ├── __init__.py
│       ├── connection.py       # Top Connection Panel & LED indicator
│       ├── image_view.py       # Image Studio Pillow composer & progress bar
│       ├── text_view.py        # Text Note Editor tab
│       ├── file_view.py        # Generic File Picker dialog tab
│       └── hex_view.py         # Protocol Inspector dark monospace terminal
│
├── examples/                   # Baseline Verification Scripts
│   ├── send_image.py           # End-to-end JPEG card transfer script
│   └── send_text.py            # End-to-end plain text (.txt) transfer script
│
├── tests/                      # Automated Unit Test Suite
│   └── test_packets.py         # Pure unit tests for headers, GUIDs & packets
│
├── main.py                     # Desktop GUI Application Entry Point
├── .gitignore
└── README.md
```

---

## 📊 Bluetooth Service Profile Matrix

| Service UUID | Profile Name | Current Status | Verification Evidence |
|---|---|---|---|
| **`0x1105`** | Object Push Profile (OPP) | ✅ **Fully Working** | PC $\to$ Phone JPEG & `.txt` transfer verified |
| **`0x1106`** | OBEX File Transfer (FTP) | 🧪 **Supported** | Service exposed; GET/PUT engine ready |
| **`0x112F`** | Phonebook Access (PBAP) | 🧪 **Supported** | Service exposed; vCard extraction ready |
| **`0x1101`** | Serial Port Profile (SPP) | 🔬 **Experimental** | COM5 serial port opens; echo observed |

---

## 🚦 Getting Started

### Prerequisites
- **Operating System**: Windows 10 or Windows 11
- **Python**: Python 3.10 or higher
- **Hardware**: Bluetooth Adapter (Built-in or USB Dongle) + paired Samsung GT-S3802

### Installation

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/Omii-004/S3802-BLUETOOTH-LAB.git
   cd S3802-BLUETOOTH-LAB
   ```

2. **Create and activate a virtual environment**:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```powershell
   pip install pillow
   ```

---

## 🎮 Running the Project

### 1. Launch the Desktop GUI Application
```powershell
python main.py
```

### 2. Run Automated Unit Tests (No phone required)
```powershell
python -m unittest discover tests
```

### 3. Run Standalone Verification Scripts
```powershell
# Send test JPEG card
python examples/send_image.py

# Send text note (.txt)
python examples/send_text.py
```

---

## 📝 License & Disclaimer

This project is open-source research and interoperability software. It operates strictly within standard IrDA OBEX and Bluetooth RFCOMM specifications without modifying phone firmware or bootloaders.
