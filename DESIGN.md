# S3802-Bluetooth-Lab: Desktop Application & GUI Design

## 1. UX Strategy & Architecture
The `S3802 Desktop Controller` transforms prototype command-line scripts into an operator-grade desktop control suite using Python's standard `tkinter` and `tkinter.ttk` libraries.

### Core GUI Principles:
1. **Zero UI Freezes (Asynchronous Threading)**: Bluetooth socket operations (`connect`, `send`, `recv`) are synchronous and blocking. If executed on the GUI event loop thread, the window will stop responding and Windows will mark it as "Not Responding". Therefore, all network and device operations execute inside isolated daemon worker threads, communicating status to the UI through thread-safe `queue.Queue` channels.
2. **Visual Transparency**: Low-level protocol reverse engineering requires constant feedback. The GUI embeds a live hexadecimal terminal displaying every raw byte sent (`TX`) and received (`RX`).
3. **Responsive Visual Composition**: An integrated Image Generator allows composing text cards and converting them to S3802-compatible 800x480 JPEGs with real-time on-screen preview before initiating the transfer.

---

## 2. Window Layout & Component Hierarchy

```
+=============================================================================+
| [TITLE BAR] S3802 Bluetooth Controller & Protocol Lab             [_][O][X] |
+=============================================================================+
| +-- [TOP PANEL: CONNECTION BAR] ------------------------------------------+ |
| | Target MAC: [ 64:B3:10:24:36:66 ]  Service: [ OPP (0x1105)        |v]   | |
| | [ Connect ]  [ Disconnect ]          Status: (● CONNECTED)   MTU: 64,512| |
| +-------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------+
| +-- [NOTEBOOK TAB NAVIGATION] --------------------------------------------+ |
| | [ 🖼 Image Studio ] | [ 📁 File Transfer ] | [ 📇 Phonebook ] | [ 🔍 Hex Log ]| |
| +-------------------------------------------------------------------------+ |
| |                                                                         | |
| |  [TAB 1: IMAGE STUDIO CONTENT]                                          | |
| |  +-----------------------------------+  +----------------------------+  | |
| |  |                                   |  | Card Title:                |  | |
| |  |                                   |  | [ HELLO FROM PYTHON      ] |  | |
| |  |          PILLOW CANVAS            |  | Subtitle / Details:        |  | |
| |  |             PREVIEW               |  | [ Samsung S3802 Lab Test ] |  | |
| |  |           (800 x 480)             |  | Footer:                    |  | |
| |  |                                   |  | [ NO INTERNET REQUIRED   ] |  | |
| |  |                                   |  |                            |  | |
| |  |                                   |  | [ Update Preview ]         |  | |
| |  +-----------------------------------+  | [ 🚀 Send to S3802 ]       |  | |
| |                                         +----------------------------+  | |
| |  Transfer Progress: [====================================>     ] 74%     | |
| +-------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------+
| +-- [BOTTOM PANEL: PROTOCOL LOG MONITOR] ---------------------------------+ |
| | [13:20:01.102] TX -> 80 00 07 10 00 20 00                               | |
| | [13:20:01.240] RX <- A0 00 07 10 00 FC 00 (OBEX Success, Max: 64,512 B) | |
| | [13:20:01.310] TX -> 82 00 2B 01 00 14 00 74 00 65 00 73 00 74 ...     | |
| | [13:20:02.890] RX <- A0 00 03 (PUT Complete: Accepted by S3802)          | |
| +-------------------------------------------------------------------------+ |
+=============================================================================+
```

---

## 3. UI Component Specifications

### 3.1 Connection Bar (`gui/views/connection.py`)
- **Device MAC Input**: Text entry pre-populated with `"64:B3:10:24:36:66"`, supporting fast recall of recent addresses.
- **Service Selector**: Dropdown (`ttk.Combobox`) selecting target service UUID:
  - `OPP (0x1105)` - Object Push (Active/Proven)
  - `FTP (0x1106)` - File Transfer Profile (Phase 3)
  - `PBAP (0x112F)` - Phonebook Access (Phase 3)
  - `SPP (0x1101)` - Serial Port Profile (Phase 3)
- **Status Indicator**: Dynamic Canvas circle (Green = Connected, Orange = Connecting, Red = Disconnected) with descriptive text label.

### 3.2 Image Studio Tab (`gui/views/image_push.py`)
- **Canvas Preview Area**: A scaled `tkinter.Canvas` (e.g., 400x240 preview of the 800x480 rendering target).
- **Text Controls**: Three input fields (Header, Body, Footer) updating text rendered via Pillow.
- **Render Engine**: Generates high-quality JPEGs using `PIL.Image`, `PIL.ImageDraw`, and `PIL.ImageFont`.
- **Push Button**: Emits a transfer job to the background thread, chunking the image bytes into OBEX PUT packets.

### 3.3 File Transfer Tab (`gui/views/file_transfer.py`)
- **File Chooser**: System file dialog (`filedialog.askopenfilename`) allowing any file to be selected.
- **File Meta Card**: Displays filename, byte size, detected MIME type, and expected packet count.
- **Progress Gauge**: `ttk.Progressbar` linked to packet acknowledgment updates (`0x90 Continue` -> increment bar).

### 3.4 Protocol Log Monitor (`gui/views/hex_monitor.py`)
- **ScrolledText Console**: High-performance monospace text buffer (`Consolas` or `Courier New`).
- **Color-Coded Protocol Highlighting**:
  - `TX` (Outgoing): Blue (`#0066cc`)
  - `RX` (Incoming): Green (`#008800`)
  - `ERR` (Winsock/OBEX Errors): Red (`#cc0000`)
  - `INFO` (System State Changes): Gray (`#666666`)
- **Controls**: "Clear Log" and "Export Log to File" buttons.

---

## 4. Multi-Threading & Concurrency Model

```
   [ UI Thread (Main) ]                     [ Background Worker Thread ]
           |                                             |
   (User clicks "Send")                                  |
           |                                             |
           |---- Enqueue Job (payload, service) -------->|
           |                                             |-- Establish Socket
           |                                             |-- Send OBEX CONNECT
           |                                             |-- Wait for 0xA0
           |<--- Post Log Event (TX/RX Hex) -------------|
   (Render Hex Log)                                      |
           |                                             |-- Chunk & Send OBEX PUT
           |<--- Post Progress Update (chunk %) ---------|
   (Update Progressbar)                                  |
           |                                             |-- Wait for Final 0xA0
           |<--- Post Complete Event --------------------|
   (Show Success Alert)                                  |
```

- **Thread Safety**: The UI thread uses `root.after(50, poll_queue)` to process events emitted by worker threads, guaranteeing thread-safe Tkinter updates.
