import time
from collections.abc import Callable
from typing import NamedTuple

from prompt_toolkit.layout.controls import FormattedTextControl, UIContent
from prompt_toolkit.mouse_events import MouseButton, MouseEvent, MouseEventType

from core.board import Board
from core.pile import Pile


class GridHit(NamedTuple):
    """Logical board coordinates mapped from a terminal (x, y) click."""

    row: int
    col: int
    card_idx: int | None = None


class MouseTextControl(FormattedTextControl):
    """FormattedTextControl that routes terminal mouse events to a callback."""

    def __init__(self, on_mouse_event: Callable[[MouseEvent], bool], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_mouse_event = on_mouse_event

    def create_content(self, width: int, height: int) -> UIContent:
        content = super().create_content(width, height)
        return UIContent(
            get_line=lambda i: [*content.get_line(i), ('', ' ')] if i < content.line_count else [('', ' ')],
            line_count=content.line_count + 1,
            show_cursor=content.show_cursor,
        )

    def mouse_handler(self, mouse_event: MouseEvent):
        return None if self.on_mouse_event(mouse_event) else NotImplemented


class BoardMouseController:
    """Reusable base mouse controller for 2D grid-based card games."""

    DOUBLE_CLICK_THRESHOLD: float = 0.4

    def __init__(self, board: Board):
        self.board = board
        self._last_click: tuple[float, GridHit] | None = None

    def reset(self) -> None:
        self._last_click = None

    def hit_test(self, x: int, y: int) -> GridHit | None:
        """Return GridHit only if (x, y) is strictly inside a navigable pile/card."""
        if x < 0 or y < 0 or not self.board.board:
            return None

        col = x // Pile.WIDTH
        y_start = self.board.get_header_height()
        if y < y_start:
            return None

        for row_idx, row in enumerate(self.board.board):
            row_height = self.board.get_row_height(row_idx)
            if y < y_start + row_height:
                if not (0 <= col < len(row)) or not self.board.is_navigable(row_idx, col):
                    return None

                y_offset = y - y_start
                pile = row[col]
                if y_offset <= 0 or y_offset >= pile.get_height() - 1:
                    return None

                if not pile.stretched or pile.is_empty():
                    return GridHit(row_idx, col)

                card_idx = pile.get_card_at_offset(y_offset)
                if card_idx is None:
                    return None
                return GridHit(row_idx, col, card_idx)

            y_start += row_height

        return None

    def _is_double_click(self, hit: GridHit) -> bool:
        now = time.monotonic()
        is_double = (
            self._last_click is not None
            and (now - self._last_click[0] < self.DOUBLE_CLICK_THRESHOLD)
            and self._last_click[1] == hit
        )
        self._last_click = (now, hit)
        return is_double

    def handle_mouse(self, mouse_event: MouseEvent) -> bool:
        if mouse_event.event_type != MouseEventType.MOUSE_UP or mouse_event.button != MouseButton.LEFT:
            return False
        hit = self.hit_test(mouse_event.position.x, mouse_event.position.y)
        if hit is None:
            return False

        if self._is_double_click(hit):
            self.reset()
            if self.on_double_click(hit):
                return True

        return self.on_click(hit)

    def on_click(self, hit: GridHit) -> bool:
        """Default handler navigates cursor to the clicked pile."""
        self.board.navigate_to_coordinate(hit.row, hit.col)
        return True

    def on_double_click(self, hit: GridHit) -> bool:
        """Override in subclasses to handle a double left click."""
        return False
