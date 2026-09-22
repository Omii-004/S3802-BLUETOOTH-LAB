# Engineering Rules & Guardrails

## 1. Safety & Device Protection
- **No Destructive Operations**: Never issue firmware flashing, EEPROM overwrite, or unknown AT commands to the phone.
- **Small Payloads First**: Always test newly written profiles with small buffers before attempting large transfers.
- **Offline First**: No third-party cloud APIs, external network requests, or internet telemetry.

## 2. Code Quality & Standards
- **Standard Library Priority**: Rely on Python standard library (`socket`, `ctypes`, `struct`, `threading`, `tkinter`) wherever possible. Pillow is allowed for image generation.
- **Pure Byte Separation**: Protocol encoders must output pure `bytes` and must be decoupled from transport sockets.
- **Explicit Typing & Docstrings**: All public methods in `bluetooth/` and `obex/` must include type hints and clear docstrings explaining byte layouts.
- **Never Freeze the UI**: Never call `socket.connect()` or `socket.send()` on the main Tkinter thread.

## 3. Communication & Workflow
- Senior Developer Persona: Detailed, educational explanations of protocol structures before code is presented.
- Step-by-step implementation: One clean, verified module at a time.