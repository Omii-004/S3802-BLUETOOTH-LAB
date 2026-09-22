"""
examples/send_image.py
======================
End-to-end baseline verification script.
Generates a custom JPEG card and sends it to Samsung GT-S3802 over OPP.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from bluetooth.device import S3802Device
from services.opp import ObjectPushService

PHONE_MAC = "64:B3:10:24:36:66"


def create_test_card() -> bytes:
    """Generate 800x480 test image card using Pillow."""
    img = Image.new("RGB", (800, 480), "white")
    draw = ImageDraw.Draw(img)

    try:
        font_lg = ImageFont.truetype("arial.ttf", 50)
        font_sm = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        font_lg = font_sm = ImageFont.load_default()

    draw.text((400, 100), "S3802 MODULAR ENGINE", fill="black", font=font_lg, anchor="mm")
    draw.text((400, 200), "Status: Verified & Operational", fill="blue", font=font_sm, anchor="mm")
    draw.text((400, 280), "Text Files: Fully Supported!", fill="green", font=font_sm, anchor="mm")
    draw.text((400, 380), "NO INTERNET REQUIRED", fill="black", font=font_sm, anchor="mm")

    output_path = Path("test_card.jpg")
    img.save(output_path, "JPEG", quality=90)
    return output_path.read_bytes()


def main():
    print("==================================================")
    print(" S3802 Bluetooth OPP Baseline Transfer Test")
    print("==================================================")

    device = S3802Device(PHONE_MAC)
    opp = ObjectPushService(device)

    try:
        print(f"Connecting to {PHONE_MAC} on OPP service (0x1105)...")
        if opp.connect():
            print(f"[SUCCESS] Connected & Negotiated MTU: {opp.max_packet_len} bytes")

            image_bytes = create_test_card()
            print("Sending 'test_card.jpg' to phone...")

            def progress(current, total):
                pct = int((current / total) * 100)
                print(f"  Transfer Progress: {current}/{total} bytes ({pct}%)")

            success = opp.push_image("test_card.jpg", image_bytes)
            if success:
                print("\n[SUCCESS] Image transferred successfully to Samsung GT-S3802!")
            else:
                print("\n[ERROR] Phone rejected the file transfer.")
    finally:
        device.disconnect()
        print("Disconnected cleanly.")


if __name__ == "__main__":
    main()