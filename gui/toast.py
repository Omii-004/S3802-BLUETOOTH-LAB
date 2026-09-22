"""
gui/toast.py
============
Floating in-app toast notification banner widget.
Displays sleek success/error notification toasts without window flickering.
"""

import tkinter as tk
from gui.theme import Colors


class ToastNotification:
    """Floating banner toast notification inside the desktop app window."""

    def __init__(self, parent_window: tk.Tk):
        self.parent = parent_window

    def show(self, message: str, is_error: bool = False, duration_ms: int = 5000):
        """Display a smooth floating toast banner message at the bottom right corner."""
        toast = tk.Toplevel(self.parent)
        toast.withdraw()  # Hide window immediately to prevent top-left flickering
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)

        bg_color = Colors.ACCENT_RED if is_error else Colors.ACCENT_GREEN
        fg_color = "#FFFFFF" if is_error else "#000000"
        icon = "❌ " if is_error else "✅ "

        outer_frame = tk.Frame(toast, bg="#000000", padx=1, pady=1)
        outer_frame.pack()

        frame = tk.Frame(outer_frame, bg=bg_color, padx=22, pady=12)
        frame.pack()

        lbl = tk.Label(
            frame,
            text=icon + message,
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 10, "bold"),
        )
        lbl.pack()

        # Update layout to measure exact width & height before showing
        toast.update_idletasks()
        req_w = toast.winfo_reqwidth()
        req_h = toast.winfo_reqheight()

        # Calculate exact bottom-right position relative to parent window
        self.parent.update_idletasks()
        px = self.parent.winfo_x() + self.parent.winfo_width() - req_w - 20
        py = self.parent.winfo_y() + self.parent.winfo_height() - req_h - 20

        toast.geometry(f"{req_w}x{req_h}+{px}+{py}")
        toast.deiconify()  # Smoothly reveal window at exact position!

        # Auto-destroy after 5 seconds
        toast.after(duration_ms, toast.destroy)