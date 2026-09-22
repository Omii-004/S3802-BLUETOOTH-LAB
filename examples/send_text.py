"""
examples/send_text.py
=====================
Verification script for sending plain text (.txt) files to Samsung GT-S3802 over OBEX OPP.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bluetooth.device import S3802Device
from services.opp import ObjectPushService

PHONE_MAC = "64:B3:10:24:36:66"

SAMPLE_TEXT = """==================================
  S3802 BLUETOOTH LAB - TEXT TEST
==================================

Hello from Python!

This text document was transferred offline
over Bluetooth RFCOMM using the custom OBEX
Object Push Profile engine.

Status: TXT Reading Confirmed Operational!
"""


def main():
    print("==================================================")
    print(" S3802 Bluetooth OPP Text File (.txt) Transfer")
    print("==================================================")

    device = S3802Device(PHONE_MAC)
    opp = ObjectPushService(device)

    try:
        print(f"Connecting to {PHONE_MAC} on OPP service (0x1105)...")
        if opp.connect():
            print(f"[SUCCESS] Connected & Negotiated MTU: {opp.max_packet_len} bytes")

            filename = "note.txt"
            print(f"Sending '{filename}' to phone...")

            success = opp.push_text(filename, SAMPLE_TEXT)
            if success:
                print(f"\n[SUCCESS] '{filename}' transferred successfully!")
                print("Check your Samsung S3802 display/inbox to view the text note.")
            else:
                print("\n[ERROR] Phone rejected the text file transfer.")
    finally:
        device.disconnect()
        print("Disconnected cleanly.")


if __name__ == "__main__":
    main()