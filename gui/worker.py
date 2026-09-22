"""
gui/worker.py
=============
Asynchronous background task worker thread for Bluetooth I/O operations.
Prevents blocking or freezing the Tkinter main event loop.
"""

from queue import Queue
import threading
from typing import Callable, NamedTuple, Optional


class WorkerTask(NamedTuple):
    func: Callable
    args: tuple
    kwargs: dict
    on_success: Optional[Callable]
    on_error: Optional[Callable]


class AsyncWorker:
    """Worker thread manager for non-blocking execution of Bluetooth socket calls."""

    def __init__(self):
        self.task_queue: Queue[WorkerTask] = Queue()
        self._thread: Optional[threading.Thread] = None
        self._running = True
        self._start_worker()

    def _start_worker(self):
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()

    def _worker_loop(self):
        while self._running:
            task = self.task_queue.get()
            if task is None:
                break
            try:
                result = task.func(*task.args, **task.kwargs)
                if task.on_success:
                    task.on_success(result)
            except Exception as exc:
                if task.on_error:
                    task.on_error(exc)
            finally:
                self.task_queue.task_done()

    def submit(
        self,
        func: Callable,
        *args,
        on_success: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        **kwargs,
    ):
        """Enqueue a background task for asynchronous execution."""
        task = WorkerTask(
            func=func,
            args=args,
            kwargs=kwargs,
            on_success=on_success,
            on_error=on_error,
        )
        self.task_queue.put(task)

    def stop(self):
        self._running = False
        self.task_queue.put(None)