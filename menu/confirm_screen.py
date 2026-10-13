from collections.abc import Callable

from menu.base import ScreenItem, SelectableScreen


class ConfirmScreen(SelectableScreen):
    """Confirmation dialog screen for destructive or important actions."""

    items: tuple[ScreenItem, ...] = (
        ScreenItem('y', 'Yes'),
        ScreenItem('n', 'No'),
    )
    selected_idx: int = 1
    hints: tuple[ScreenItem, ...] = (
        ScreenItem('Enter', 'Select'),
        ScreenItem('Esc', 'Cancel'),
    )

    def __init__(self, message: str, on_close: Callable[[bool], None]) -> None:
        super().__init__(on_select=lambda item: on_close(item.key == 'y'))
        self.title = f'♠   ♥   {message}   ♦   ♣'

        @self.kb.add('escape')
        def _(event):
            on_close(False)
