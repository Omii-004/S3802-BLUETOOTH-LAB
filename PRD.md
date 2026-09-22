# Product Requirements Document (PRD)

## Project Title
**S3802-Bluetooth-Lab & Desktop Controller**

## 1. Objective & Vision
Repurpose a legacy Samsung GT-S3802 feature phone into a programmable offline peripheral and secondary display controlled by a modern Windows PC over Bluetooth RFCOMM and OBEX protocols. The system must operate 100% offline without requiring Wi-Fi, cellular data, or internet connectivity.

## 2. Target Persona & Use Cases
- **Embedded / Systems Developer**: Protocol analysis, OBEX reverse engineering, service profiling.
- **Desktop User**: An intuitive Tkinter desktop GUI to pair, browse phone services, push images/notes, query contacts, and view transfer status in real-time.

## 3. Scope & Phased Feature Requirements

### Phase 1: Foundation (Completed Baseline)
- [x] Enumerate Bluetooth services via Windows Native Winsock.
- [x] Connect to Object Push Profile (OPP UUID `0x1105`) using service UUID resolution.
- [x] Perform OBEX CONNECT handshake (`0xA0` Success).
- [x] Push JPEG images via OBEX PUT that display on the phone screen.

### Phase 2: Core Transport & Bidirectional OBEX (In Progress)
- [ ] Decoupled, modular Python transport package (`bluetooth/winsock.py`).
- [ ] Protocol engine for OBEX packet serialization and header decoding (`obex/`).
- [ ] Robust multi-packet chunking with `0x90 Continue` handling for payloads > 64 KB.
- [ ] OBEX GET implementation to pull files/objects from phone to PC.

### Phase 3: Profile Exploration & Phone Data
- [ ] OBEX File Transfer Profile (FTP UUID `0x1106`): folder navigation, directory listing (`x-obex/folder-listing`).
- [ ] Phonebook Access Profile (PBAP UUID `0x112F`): contact retrieval (`telecom/pb.vcf`).
- [ ] Serial Port Profile (SPP UUID `0x1101`): AT command evaluation / terminal bridge.

### Phase 4: Desktop Application (Tkinter GUI)
- [ ] Connection control panel (MAC address input, device status indicator, connect/disconnect).
- [ ] Image & Canvas Studio: generate or select images, preview layout (800x480 or scaled to S3802 display), push to device.
- [ ] File Transfer & Explorer tab: drag-and-drop file sender, progress bar, OBEX status log.
- [ ] Protocol Inspector tab: live raw hex transmission/reception dump (`TX` / `RX`).

## 4. Non-Functional Requirements
- **Zero Internet Dependency**: Must work in completely air-gapped environments.
- **Native Windows Compatibility**: Python 3.10+ using `ctypes` over `ws2_32.dll` (no legacy PyBluez / `use_2to3` dependencies).
- **Graceful Failure Handling**: Winsock error translation (e.g., 10049, 10054) into clear UI notifications.
- **Safety**: No firmware flashing, bootloader tampering, or destructive AT commands.