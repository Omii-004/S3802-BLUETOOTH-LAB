# Project Work Breakdown Document (PWD)

## Milestone Roadmap & Deliverables

### Milestone 1: Modular Engine Refactoring (Target: v0.1.0)
- **Deliverable 1.1**: `bluetooth/winsock.py` — Raw ctypes wrapper for Winsock `AF_BTH`, `BTHPROTO_RFCOMM`, `SOCKADDR_BTH`, GUIDs.
- **Deliverable 1.2**: `bluetooth/device.py` — High-level `S3802` class managing connection lifecycle.
- **Deliverable 1.3**: `obex/headers.py` & `obex/packet.py` — Header encoders (Name, Type, Length, Body) and packet assemblers.
- **Deliverable 1.4**: `obex/connect.py` & `obex/put.py` — Decoupled session handshake and chunked file transfer.
- **Deliverable 1.5**: `examples/send_image.py` — Verification script matching prototype baseline.
- **Deliverable 1.6**: `tests/test_packets.py` — Pure unit tests for byte structures without phone requirement.

### Milestone 2: Protocol Expansion (Target: v0.2.0)
- **Deliverable 2.1**: `obex/get.py` — Multi-packet GET request handler.
- **Deliverable 2.2**: `services/ftp.py` — OBEX FTP service exploration (`0x1106`).
- **Deliverable 2.3**: `services/pbap.py` — PBAP vCard client (`0x112F`).

### Milestone 3: Desktop GUI Application (Target: v0.3.0)
- **Deliverable 3.1**: `gui/app.py` — Main Tkinter application window with modern styling.
- **Deliverable 3.2**: `gui/views/connection.py` — Device scanner and connection management widget.
- **Deliverable 3.3**: `gui/views/image_push.py` — Canvas generator, text-to-image preview, and sender.
- **Deliverable 3.4**: `gui/views/file_transfer.py` — File picker, transfer progress bar, and status readout.
- **Deliverable 3.5**: `gui/views/hex_monitor.py` — Real-time protocol hex dump window.

### Milestone 4: Documentation & Packaging (Target: v1.0.0)
- **Deliverable 4.1**: Complete technical documentation in `docs/`.
- **Deliverable 4.2**: `pyproject.toml` and clean setup dependencies.
- **Deliverable 4.3**: Standalone executable bundling with PyInstaller (optional).