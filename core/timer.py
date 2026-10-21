from __future__ import annotations

import time


class GameTimer:
    """
    Elapsed time tracker for game sessions.

    Supports starting, stopping/freezing on game completion,
    resetting, and formatting elapsed time as mm:ss or hh:mm:ss.
    """

    start_time: float | None
    end_time: float | None

    def __init__(self, start_now: bool = True):
        self.reset(start_now=start_now)

    def __str__(self) -> str:
        return self.formatted_time()

    def __repr__(self) -> str:
        return f'GameTimer(elapsed={self.formatted_time()!r}, is_running={self.is_running})'

    @property
    def is_running(self) -> bool:
        """True if the timer is actively counting elapsed time."""
        return self.start_time is not None and self.end_time is None

    def start(self):
        """Start the timer."""
        self.start_time = time.monotonic()
        self.end_time = None

    def stop(self):
        """Freeze elapsed time (e.g. upon victory or game over)."""
        if self.is_running:
            self.end_time = time.monotonic()

    def reset(self, start_now: bool = True):
        """Reset the timer to 0."""
        self.start_time = time.monotonic() if start_now else None
        self.end_time = None

    @property
    def elapsed_seconds(self) -> int:
        """Return total elapsed whole seconds."""
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time is not None else time.monotonic()
        return max(0, int(end - self.start_time))

    def formatted_time(self) -> str:
        """Return elapsed time formatted as mm:ss (or hh:mm:ss if >= 1 hour)."""
        mins, secs = divmod(self.elapsed_seconds, 60)
        hrs, mins = divmod(mins, 60)
        if hrs > 0:
            return f'{hrs:02d}:{mins:02d}:{secs:02d}'
        return f'{mins:02d}:{secs:02d}'
