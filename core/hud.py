from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from termcolor import colored

from core.utils import format_border, strip_ansi


@dataclass(frozen=True)
class HUDItem:
    """A single labeled game statistic or HUD item."""

    label: str
    value: Any
    color: str | None = None

    def render(self, color: bool = True) -> str:
        """Render the item as a formatted 'label: value' string."""
        val = str(self.value() if callable(self.value) else self.value)
        if color and self.color:
            val = colored(val, self.color, force_color=True)
        return f'{self.label}: {val}' if self.label else val


def format_stat_row(items: Sequence[HUDItem], width: int, color: bool = True) -> str:
    """
    Format stats into a single line spaced to fit width.

    Two items are left- and right-aligned; three or more are evenly distributed.
    """
    rendered = [item.render(color=color) for item in items]
    if not rendered:
        return ''
    if len(rendered) == 1:
        return rendered[0]

    gaps = len(rendered) - 1
    remaining_spaces = width - sum(len(strip_ansi(it)) for it in rendered)
    if remaining_spaces < gaps:
        return '   '.join(rendered)

    base_gap, extra = divmod(remaining_spaces, gaps)
    parts: list[str] = []
    for idx, text in enumerate(rendered):
        parts.append(text)
        if idx < gaps:
            gap_size = base_gap + (1 if idx < extra else 0)
            parts.append(' ' * gap_size)
    return ''.join(parts)


def render_hud(items: Sequence[HUDItem], width: int) -> list[str]:
    """Render bordered 4-line HUD header if items present, else empty list."""
    if not items:
        return []
    stat_line = format_stat_row(items, width)
    box_width = max(width, len(strip_ansi(stat_line)))
    border = format_border(box_width)
    return [border, stat_line, border, '']
