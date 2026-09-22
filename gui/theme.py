"""
gui/theme.py
============
Modern dark theme design system and ttk style configurator.
Provides colors, fonts, and custom widget styles for S3802 Desktop Controller.
"""

import tkinter as tk
from tkinter import ttk


class Colors:
    """Cyber-Dark Color Palette."""
    BG_DARK = "#121214"          # Deep Space Background
    BG_CARD = "#1E1E24"          # Panel / Card Background
    BG_CARD_BORDER = "#2A2A34"   # Border Outline
    BG_INPUT = "#18181C"         # Text Input Background

    TEXT_MAIN = "#F4F4F5"        # Main Typography
    TEXT_MUTED = "#A1A1AA"       # Secondary Labels

    ACCENT_CYAN = "#00E5FF"      # Cyan Accent (Buttons & Glows)
    ACCENT_GREEN = "#00E676"     # Connected / Success Accent
    ACCENT_PURPLE = "#7C4DFF"    # Special Action Accent
    ACCENT_RED = "#FF5252"       # Error Accent
    ACCENT_ORANGE = "#FF9100"    # Warning / Connecting Accent


def apply_modern_theme(root: tk.Tk):
    """Apply modern dark theme styling to Tkinter root and ttk widgets."""
    root.configure(bg=Colors.BG_DARK)

    style = ttk.Style(root)
    style.theme_use("clam")

    # Configure Base Styles
    style.configure(".", background=Colors.BG_DARK, foreground=Colors.TEXT_MAIN, font=("Segoe UI", 9))

    # Frame & LabelFrame Styling
    style.configure("TFrame", background=Colors.BG_DARK)
    style.configure(
        "TLabelframe",
        background=Colors.BG_CARD,
        foreground=Colors.ACCENT_CYAN,
        bordercolor=Colors.BG_CARD_BORDER,
        relief="solid",
        borderwidth=1,
    )
    style.configure("TLabelframe.Label", background=Colors.BG_CARD, foreground=Colors.ACCENT_CYAN, font=("Segoe UI", 9, "bold"))

    # Label Styling
    style.configure("TLabel", background=Colors.BG_CARD, foreground=Colors.TEXT_MAIN)
    style.configure("Muted.TLabel", foreground=Colors.TEXT_MUTED)

    # Entry Field Styling
    style.configure(
        "TEntry",
        fieldbackground=Colors.BG_INPUT,
        foreground=Colors.TEXT_MAIN,
        bordercolor=Colors.BG_CARD_BORDER,
        insertcolor=Colors.TEXT_MAIN,
        padding=5,
    )

    # Button Styling
    style.configure(
        "TButton",
        background=Colors.BG_CARD_BORDER,
        foreground=Colors.TEXT_MAIN,
        bordercolor=Colors.ACCENT_CYAN,
        font=("Segoe UI", 9, "bold"),
        padding=6,
    )
    style.map(
        "TButton",
        background=[("active", Colors.ACCENT_CYAN), ("disabled", "#27272A")],
        foreground=[("active", "#000000"), ("disabled", "#71717A")],
    )

    # Notebook Tabs Styling
    style.configure(
        "TNotebook",
        background=Colors.BG_DARK,
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        background=Colors.BG_CARD,
        foreground=Colors.TEXT_MUTED,
        padding=[14, 8],
        font=("Segoe UI", 9, "bold"),
        bordercolor=Colors.BG_CARD_BORDER,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", Colors.BG_CARD_BORDER)],
        foreground=[("selected", Colors.ACCENT_CYAN)],
    )

    # Progress Bar Styling
    style.configure(
        "Horizontal.TProgressbar",
        troughcolor=Colors.BG_INPUT,
        background=Colors.ACCENT_CYAN,
        bordercolor=Colors.BG_CARD_BORDER,
        thickness=10,
    )