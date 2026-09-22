"""
gui/views/hex_view.py
======================
Real-time protocol inspector view.
Displays color-coded hex stream dumps (TX in Blue, RX in Green, ERR in Red).
"""

import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText

from gui.logger import LogEvent, LogLevel


class HexMonitorView(ttk.LabelFrame):
    """Protocol inspector frame displaying real-time raw byte transmissions."""

    def __init__(self, parent):
        super().__init__(parent, text=" Live Protocol Hex Stream Inspector ", padding=8)

        # Monospace Text Terminal
        self.txt_console = ScrolledText(
            self,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=10,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
        )
        self.txt_console.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        # Syntax Color Tags
        self.txt_console.tag_config("TX", foreground="#569cd6")       # Light Blue
        self.txt_console.tag_config("RX", foreground="#6a9955")       # Soft Green
        self.txt_console.tag_config("ERROR", foreground="#f44747")    # Bright Red
        self.txt_console.tag_config("SUCCESS", foreground="#4ec9b0")  # Teal/Cyan
        self.txt_console.tag_config("INFO", foreground="#9cdcfe")     # Ice Blue

        # Bottom Button Bar
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))

        ttk.Button(btn_frame, text="Clear Log", command=self.clear_log).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Export Log...", command=self.export_log).pack(side=tk.RIGHT, padx=5)

    def append_log(self, event: LogEvent):
        """Append a structured LogEvent to the monospace terminal."""
        line = f"[{event.timestamp}] [{event.level:7s}] {event.message}\n"
        if event.hex_dump:
            line += f"  HEX: {event.hex_dump}\n"

        self.txt_console.insert(tk.END, line, event.level)
        self.txt_console.see(tk.END)  # Auto-scroll to latest log entry

    def clear_log(self):
        """Clear all entries from the terminal window."""
        self.txt_console.delete("1.0", tk.END)

    def export_log(self):
        """Save terminal content to a text file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("Text Files", "*.txt")],
        )
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.txt_console.get("1.0", tk.END))