"""
gui/views/file_view.py
======================
Generic File Transfer tab.
Allows selecting any local file (images, docs) and pushing it to S3802.
"""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable


class FilePusherView(ttk.Frame):
    """File selection and generic uploader tab."""

    def __init__(self, parent, on_send_file: Callable[[str, bytes], None]):
        super().__init__(parent, padding=15)

        self.on_send_file_cb = on_send_file
        self.selected_path: str = ""

        # File Picker Bar
        picker_frame = ttk.LabelFrame(self, text=" Select File to Transfer ", padding=10)
        picker_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))

        self.entry_path = ttk.Entry(picker_frame, width=40)
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        ttk.Button(picker_frame, text="Browse...", command=self._browse_file).pack(side=tk.LEFT)

        # Meta Info Label
        self.lbl_meta = ttk.Label(self, text="No file selected.", foreground="gray")
        self.lbl_meta.pack(anchor="w", pady=(0, 15))

        # Send Button
        self.btn_send = ttk.Button(
            self, text="📤 Push Selected File to S3802", command=self._handle_send, state="disabled"
        )
        self.btn_send.pack(anchor="w")

    def _browse_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.selected_path = path
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, path)

            p = Path(path)
            size_kb = p.stat().st_size / 1024
            self.lbl_meta.config(
                text=f"Selected: {p.name} ({size_kb:.1f} KB)", foreground="black"
            )
            self.btn_send.config(state="normal")

    def _handle_send(self):
        if self.selected_path:
            p = Path(self.selected_path)
            data = p.read_bytes()
            self.on_send_file_cb(p.name, data)