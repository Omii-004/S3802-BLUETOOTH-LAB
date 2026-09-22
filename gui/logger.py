"""
gui/logger.py
=============
Thread-safe event logging queue and LogEvent structures.
Allows background Bluetooth workers to pass TX/RX hex dumps and status events to the UI.
"""

from datetime import datetime
from queue import Queue
from typing import NamedTuple, Optional


class LogLevel:
    INFO = "INFO"
    TX = "TX"
    RX = "RX"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class LogEvent(NamedTuple):
    timestamp: str
    level: str
    message: str
    hex_dump: Optional[str] = None


class GuiLogger:
    """Thread-safe event logger backing the UI Protocol Hex Monitor."""

    def __init__(self):
        self.queue: Queue[LogEvent] = Queue()

    def log(self, level: str, message: str, hex_dump: Optional[str] = None):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        event = LogEvent(timestamp=ts, level=level, message=message, hex_dump=hex_dump)
        self.queue.put(event)

    def log_tx(self, message: str, data: bytes):
        self.log(LogLevel.TX, message, hex_dump=data.hex(" ").upper())

    def log_rx(self, message: str, data: bytes):
        self.log(LogLevel.RX, message, hex_dump=data.hex(" ").upper())

    def log_error(self, message: str):
        self.log(LogLevel.ERROR, message)

    def log_info(self, message: str):
        self.log(LogLevel.INFO, message)

    def log_success(self, message: str):
        self.log(LogLevel.SUCCESS, message)