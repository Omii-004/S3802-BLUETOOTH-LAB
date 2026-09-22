"""
gui/views/image_view.py
========================
Image Studio tab.
Provides text-to-card composition, Pillow 800x480 JPEG rendering,
live canvas preview, and one-click transmission to Samsung GT-S3802.
"""

from io import BytesIO
import tkinter as tk
from tkinter import ttk
from typing import Callable, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageTk


class ImageStudioView(ttk.Frame):
    """Image composer and preview widget for S3802 display cards."""

    def __init__(self, parent, on_send_image: Callable[[str, bytes], None]):
        super().__init__(parent, padding=10)

        self.on_send_image_cb = on_send_image
        self.preview_photo = None

        # Grid Layout: Left Canvas Preview, Right Control Panel
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Left Side: Canvas Preview (400x240 representing 800x480 card)
        preview_frame = ttk.LabelFrame(self, text=" Live Card Preview (800x480) ", padding=5)
        preview_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.canvas = tk.Canvas(preview_frame, width=400, height=240, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Right Side: Text Controls
        controls_frame = ttk.LabelFrame(self, text=" Card Content Controls ", padding=10)
        controls_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Label(controls_frame, text="Header Title:").pack(anchor="w", pady=(0, 2))
        self.entry_title = ttk.Entry(controls_frame, width=30)
        self.entry_title.insert(0, "S3802 DESKTOP CONTROL")
        self.entry_title.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(controls_frame, text="Subtitle Line:").pack(anchor="w", pady=(0, 2))
        self.entry_sub = ttk.Entry(controls_frame, width=30)
        self.entry_sub.insert(0, "Offline Bluetooth Transfer")
        self.entry_sub.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(controls_frame, text="Footer Note:").pack(anchor="w", pady=(0, 2))
        self.entry_footer = ttk.Entry(controls_frame, width=30)
        self.entry_footer.insert(0, "NO INTERNET REQUIRED")
        self.entry_footer.pack(fill=tk.X, pady=(0, 12))

        ttk.Button(controls_frame, text="Update Preview", command=self.update_preview).pack(
            fill=tk.X, pady=4
        )
        ttk.Button(
            controls_frame, text="🚀 Send Image to S3802", command=self._handle_send
        ).pack(fill=tk.X, pady=4)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.update_preview()

    def generate_image_bytes(self) -> Tuple[bytes, Image.Image]:
        """Render 800x480 JPEG card in memory using Pillow."""
        img = Image.new("RGB", (800, 480), "white")
        draw = ImageDraw.Draw(img)

        try:
            font_lg = ImageFont.truetype("arial.ttf", 46)
            font_sm = ImageFont.truetype("arial.ttf", 30)
        except OSError:
            font_lg = font_sm = ImageFont.load_default()

        draw.text((400, 100), self.entry_title.get(), fill="black", font=font_lg, anchor="mm")
        draw.text((400, 220), self.entry_sub.get(), fill="blue", font=font_sm, anchor="mm")
        draw.text((400, 340), self.entry_footer.get(), fill="darkgreen", font=font_sm, anchor="mm")

        buf = BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return buf.getvalue(), img

    def update_preview(self):
        """Render Pillow image and scale to 400x240 for Tkinter Canvas."""
        _, img = self.generate_image_bytes()
        preview_img = img.resize((400, 240), Image.Resampling.LANCZOS)
        self.preview_photo = ImageTk.PhotoImage(preview_img)
        self.canvas.create_image(0, 0, image=self.preview_photo, anchor="nw")

    def _handle_send(self):
        img_bytes, _ = self.generate_image_bytes()
        self.on_send_image_cb("card.jpg", img_bytes)

    def set_progress(self, current: int, total: int):
        pct = int((current / max(1, total)) * 100)
        self.progress_bar["value"] = pct