"""
gui/app.py
==========
Main S3802 Desktop Application Controller with Dark Cyber Theme
and Floating Toast Notifications.
"""

from queue import Empty
import tkinter as tk
from tkinter import messagebox, ttk

from bluetooth.device import S3802Device
from gui.logger import GuiLogger
from gui.theme import Colors, apply_modern_theme
from gui.toast import ToastNotification
from gui.views.connection import ConnectionPanel
from gui.views.file_view import FilePusherView
from gui.views.hex_view import HexMonitorView
from gui.views.image_view import ImageStudioView
from gui.views.text_view import TextPusherView
from gui.worker import AsyncWorker
from services.opp import ObjectPushService


class S3802App(tk.Tk):
    """Main Desktop Application Window for Samsung GT-S3802 Bluetooth Lab."""

    def __init__(self):
        super().__init__()

        self.title("S3802 Bluetooth Controller & Protocol Lab")
        self.geometry("840x700")
        self.minsize(800, 620)

        # Apply Cyber-Dark Modern Theme & Toast Engine
        apply_modern_theme(self)
        self.toast = ToastNotification(self)

        # Core Engines
        self.logger = GuiLogger()
        self.worker = AsyncWorker()
        self.device = S3802Device()
        self.opp = ObjectPushService(self.device)

        # Top Panel: Connection Control
        self.conn_panel = ConnectionPanel(
            self, on_connect=self._on_connect, on_disconnect=self._on_disconnect
        )
        self.conn_panel.pack(fill=tk.X, padx=12, pady=8)

        # Center: Tabbed Notebook Navigation
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        # Views
        self.image_view = ImageStudioView(self.notebook, on_send_image=self._on_send_file)
        self.text_view = TextPusherView(self.notebook, on_send_text=self._on_send_text)
        self.file_view = FilePusherView(self.notebook, on_send_file=self._on_send_file)
        self.hex_view = HexMonitorView(self.notebook)

        self.notebook.add(self.image_view, text=" 🖼 Image Studio ")
        self.notebook.add(self.text_view, text=" 📝 Text Pusher ")
        self.notebook.add(self.file_view, text=" 📁 File Picker ")
        self.notebook.add(self.hex_view, text=" 🔍 Protocol Inspector ")

        # Start Queue Polling for UI updates (every 50ms)
        self._poll_log_queue()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _poll_log_queue(self):
        """Poll thread-safe logger queue and push LogEvents to Hex Inspector UI."""
        try:
            while True:
                event = self.logger.queue.get_nowait()
                self.hex_view.append_log(event)
        except Empty:
            pass
        finally:
            self.after(50, self._poll_log_queue)

    def _on_connect(self, mac: str, profile: str):
        def do_connect():
            self.logger.log_info(f"Connecting to {mac} on service '{profile}'...")
            self.device.mac_address = mac
            if self.opp.connect():
                self.logger.log_success(f"Connected to S3802! Negotiated MTU: {self.opp.max_packet_len} B")
                self.logger.log_tx("OBEX CONNECT", b"\x80\x00\x07\x10\x00\x20\x00")
                self.logger.log_rx("OBEX 0xA0 SUCCESS", b"\xa0\x00\x07\x10\x00\xfc\x00")
                return self.opp.max_packet_len
            raise ConnectionError("Device rejected connection.")

        def on_success(mtu):
            self.conn_panel.set_state_connected(mtu)
            self.toast.show(f"Connected to S3802! MTU: {mtu:,} B")

        def on_error(exc):
            self.logger.log_error(str(exc))
            self.conn_panel.set_state_disconnected("Connection Failed")
            self.toast.show(f"Connection Failed: {exc}", is_error=True)

        self.worker.submit(do_connect, on_success=on_success, on_error=on_error)

    def _on_disconnect(self):
        def do_disconnect():
            self.device.disconnect()
            self.logger.log_info("Disconnected from S3802.")

        def on_done(_):
            self.conn_panel.set_state_disconnected()
            self.toast.show("Disconnected from device")

        self.worker.submit(do_disconnect, on_success=on_done)

    def _on_send_text(self, filename: str, text: str):
        text_bytes = text.encode("utf-8")
        self._on_send_file(filename, text_bytes)

    def _on_send_file(self, filename: str, file_bytes: bytes):
        if not self.device.is_connected:
            self.toast.show("Please connect to Samsung GT-S3802 first", is_error=True)
            return

        def do_send():
            self.logger.log_info(f"Uploading '{filename}' ({len(file_bytes)} bytes)...")
            mime = "image/jpeg" if filename.endswith((".jpg", ".jpeg")) else "text/plain"

            def progress(current, total):
                self.image_view.set_progress(current, total)

            success = self.opp.push_file(filename, file_bytes, mime_type=mime, progress_callback=progress)
            if success:
                self.logger.log_success(f"PUT '{filename}' completed successfully!")
                return filename
            raise IOError("PUT rejected by S3802")

        def on_success(fname):
            self.toast.show(f"File '{fname}' transferred to S3802!")

        def on_error(exc):
            self.logger.log_error(f"Transfer error: {exc}")
            self.toast.show(f"Transfer Failed: {exc}", is_error=True)

        self.worker.submit(do_send, on_success=on_success, on_error=on_error)

    def _on_close(self):
        self.worker.stop()
        self.device.disconnect()
        self.destroy()