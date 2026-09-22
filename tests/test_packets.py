"""
tests/test_packets.py
======================
Automated unit tests for OBEX header encoding, packet framing, and Win32 conversions.
Runs completely offline without physical hardware.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from bluetooth.winsock import mac_to_bth_addr, uuid_to_guid
from obex.headers import encode_length, encode_name, encode_type, parse_headers
from obex.packet import (
    build_packet,
    parse_response,
    OPCODE_CONNECT,
    RESPONSE_SUCCESS,
)


class TestWinsockConverters(unittest.TestCase):
    """Test Win32 Bluetooth structure conversions."""

    def test_mac_conversion(self):
        mac_str = "64:B3:10:24:36:66"
        addr_int = mac_to_bth_addr(mac_str)
        self.assertEqual(addr_int, 0x64B310243666)

    def test_guid_conversion(self):
        uuid_str = "00001105-0000-1000-8000-00805F9B34FB"
        guid = uuid_to_guid(uuid_str)
        self.assertEqual(guid.Data1, 0x00001105)
        self.assertEqual(guid.Data2, 0x0000)
        self.assertEqual(guid.Data3, 0x1000)


class TestObexHeaderEncoders(unittest.TestCase):
    """Test OBEX 1.0 binary header encoders."""

    def test_encode_name(self):
        name_hdr = encode_name("test.txt")
        self.assertEqual(name_hdr[0], 0x01)  # Header ID NAME
        # Check UTF-16BE encoding for 'test.txt'
        self.assertIn(b"\x00t\x00e\x00s\x00t", name_hdr)

    def test_encode_type(self):
        type_hdr = encode_type("text/plain")
        self.assertEqual(type_hdr[0], 0x42)  # Header ID TYPE
        self.assertTrue(type_hdr.endswith(b"text/plain\x00"))

    def test_encode_length(self):
        len_hdr = encode_length(1024)
        self.assertEqual(len_hdr[0], 0xC3)  # Header ID LENGTH
        self.assertEqual(len_hdr[1:], b"\x00\x00\x04\x00")

    def test_parse_headers(self):
        hdr_bytes = encode_name("hello.txt") + encode_length(500)
        parsed = parse_headers(hdr_bytes)
        self.assertEqual(parsed[0x01], "hello.txt")
        self.assertEqual(parsed[0xC3], 500)


class TestObexPacketFraming(unittest.TestCase):
    """Test OBEX packet building and response decoding."""

    def test_build_packet(self):
        payload = b"\x10\x00\x20\x00"
        pkt = build_packet(OPCODE_CONNECT, payload)
        self.assertEqual(pkt[0], OPCODE_CONNECT)
        self.assertEqual(len(pkt), 7)  # 3 bytes header + 4 bytes payload

    def test_parse_response_success(self):
        # Simulated OBEX 0xA0 Success response
        rx_data = b"\xa0\x00\x07\x10\x00\xfc\x00"
        resp = parse_response(rx_data)
        self.assertEqual(resp.code, RESPONSE_SUCCESS)
        self.assertTrue(resp.is_success)
        self.assertFalse(resp.is_continue)
        self.assertEqual(resp.length, 7)


if __name__ == "__main__":
    unittest.main()