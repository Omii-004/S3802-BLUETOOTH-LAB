"""
gui/views/connection.py
========================
Top-bar Connection Panel widget for managing MAC address, profile UUID,
and real-time visual connection status LED indicators.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class ConnectionPanel(ttk.LabelFrame):
    """Top-bar control panel for Bluetooth device connection management."""

    def __init__(
        self,
        parent,
        on_connect: Callable[[str, str], None],
        on_disconnect: Callable[[], None],
        default_mac: str = "64:B3:10:24:36:66",
    ):
        super().__init__(parent, text=" Bluetooth Connection Control ", padding=10)

        self.on_connect_cb = on_connect
        self.on_disconnect_cb = on_disconnect

        # Device MAC Input
        ttk.Label(self, text="Target MAC:").grid(row=0, column=0, padx=5, sticky="w")
        self.mac_entry = ttk.Entry(self, width=18)
        self.mac_entry.insert(0, default_mac)
        self.mac_entry.grid(row=0, column=1, padx=5, sticky="w")

        # Profile Dropdown
        ttk.Label(self, text="Profile:").grid(row=0, column=2, padx=5, sticky="w")
        self.profile_var = tk.StringVar(value="OPP (0x1105)")
        self.profile_combo = ttk.Combobox(
            self,
            textvariable=self.profile_var,
            values=["OPP (0x1105)", "FTP (0x1106)", "PBAP (0x112F)", "SPP (0x1101)"],
            width=14,
            state="readonly",
        )
        self.profile_combo.grid(row=0, column=3, padx=5, sticky="w")

        # Connect / Disconnect Buttons
        self.btn_connect = ttk.Button(self, text="Connect", command=self._handle_connect)
        self.btn_connect.grid(row=0, column=4, padx=5)

        self.btn_disconnect = ttk.Button(
            self, text="Disconnect", command=self._handle_disconnect, state="disabled"
        )
        self.btn_disconnect.grid(row=0, column=5, padx=5)

        # LED Status Indicator Canvas (Red/Orange/Green dot)
        self.led_canvas = tk.Canvas(self, width=16, height=16, highlightthickness=0)
        self.led_canvas.grid(row=0, column=6, padx=(15, 5))
        self.led_dot = self.led_canvas.create_oval(2, 2, 14, 14, fill="red")

        # Status Text Label
        self.status_label = ttk.Label(self, text="Disconnected", font=("Segoe UI", 9, "bold"))
        self.status_label.grid(row=0, column=7, padx=5, sticky="w")

    def _handle_connect(self):
        mac = self.mac_entry.get().strip()
        profile_str = self.profile_var.get().split()[0].lower()
        self.set_state_connecting()
        self.on_connect_cb(mac, profile_str)

    def _handle_disconnect(self):
        self.on_disconnect_cb()

    def set_state_connecting(self):
        self.led_canvas.itemconfig(self.led_dot, fill="orange")
        self.status_label.config(text="Connecting...", foreground="orange")
        self.btn_connect.config(state="disabled")

    def set_state_connected(self, mtu: int = 8192):
        self.led_canvas.itemconfig(self.led_dot, fill="#00cc44")
        self.status_label.config(
            text=f"Connected (MTU: {mtu:,} B)", foreground="#00aa33"
        )
        self.btn_connect.config(state="disabled")
        self.btn_disconnect.config(state="normal")

    def set_state_disconnected(self, message: str = "Disconnected"):
        self.led_canvas.itemconfig(self.led_dot, fill="red")
        self.status_label.config(text=message, foreground="red")
        self.btn_connect.config(state="normal")
        self.btn_disconnect.config(state="disabled")