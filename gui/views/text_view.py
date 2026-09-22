"""
gui/views/text_view.py
======================
Text Note Pusher tab.
Provides multi-line text editor for drafting notes and pushing .txt files to S3802.
"""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Callable


class TextPusherView(ttk.Frame):
    """Multi-line text editor view for sending text notes over OBEX."""

    def __init__(self, parent, on_send_text: Callable[[str, str], None]):
        super().__init__(parent, padding=10)

        self.on_send_text_cb = on_send_text

        # Top Bar: Filename Entry & Push Button
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 8))

        ttk.Label(top_frame, text="Filename:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_filename = ttk.Entry(top_frame, width=20)
        self.entry_filename.insert(0, "note.txt")
        self.entry_filename.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(top_frame, text="📤 Send Text Note to S3802", command=self._handle_send).pack(
            side=tk.LEFT
        )

        # Multi-line Text Editor
        self.txt_editor = ScrolledText(
            self, wrap=tk.WORD, font=("Consolas", 10), height=12
        )
        self.txt_editor.pack(fill=tk.BOTH, expand=True)
        self.txt_editor.insert(
            tk.END,
            "S3802 BLUETOOTH LAB\n==================\n\nSent from Desktop App!\nStatus: Connected",
        )

    def _handle_send(self):
        filename = self.entry_filename.get().strip()
        content = self.txt_editor.get("1.0", tk.END).strip()
        if filename and content:
            self.on_send_text_cb(filename, content)