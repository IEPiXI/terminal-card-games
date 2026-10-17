import re
from abc import ABC
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.mouse_events import MouseEvent
from termcolor import colored

from menu.mouse import handle_menu_mouse

BORDER: str = '  O' + '=' * 69 + 'O'
SCREEN_WIDTH: int = len(BORDER)
_ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')


@dataclass(frozen=True)
class ScreenItem:
    """Selectable item or hint hotkey with a key, display label, and optional payload value."""

    key: str
    label: str
    value: str = ''

    def __post_init__(self) -> None:
        if not self.value:
            object.__setattr__(self, 'value', self.key)


def strip_ansi(text: str) -> str:
    """Return text with ANSI escape codes removed."""
    return _ANSI_ESCAPE_RE.sub('', text)


def center_line(text: str, width: int = SCREEN_WIDTH) -> str:
    """Center text across the screen width, ignoring invisible ANSI escape codes."""
    visible_length = len(strip_ansi(text))
    padding = ' ' * max(0, (width - visible_length) // 2)
    return f'{padding}{text}'


def center_block(text: str, width: int = SCREEN_WIDTH) -> str:
    """Center every non-empty line in a multiline text block."""
    return '\n'.join(center_line(line, width=width) if line.strip() else '' for line in text.strip('\n').splitlines())


def render_hints(*hints: ScreenItem, width: int = SCREEN_WIDTH) -> str:
    """Render a centered hotkey bar."""
    bar = '     '.join(f'[{h.key}] {h.label}' for h in hints)
    return center_line(bar, width=width)


def with_border(content: str) -> str:
    """Enclose screen content between top and bottom borders."""
    return f'{BORDER}\n\n{content}\n\n{BORDER}'


def colorize_suits(text: str, color: bool = True) -> str:
    """Colorize hearts and diamonds red if color is enabled."""
    if not color:
        return text
    return text.replace('♥', colored('♥', 'red')).replace('♦', colored('♦', 'red'))


class Screen(ABC):
    """Base class for full-screen terminal views."""

    banner: str = ''
    title: str = ''
    hints: tuple[ScreenItem, ...] = ()
    bordered: bool = True

    def __init__(self) -> None:
        self.kb = KeyBindings()

    def render_banner(self, color: bool = True) -> str:
        """Render pre-formatted ASCII banner graphic."""
        return colorize_suits(self.banner, color=color) if self.banner else ''

    def render_title(self, color: bool = True) -> str:
        """Render centered screen title or message."""
        return center_block(colorize_suits(self.title, color=color)) if self.title else ''

    def render_hints(self) -> str:
        """Render centered hotkey hints."""
        return render_hints(*self.hints) if self.hints else ''

    def render_content(self, color: bool = True) -> list[str]:
        """Intermediate content lines. Override in subclasses."""
        return []

    def render(self, color: bool = True) -> str:
        """Assemble banner, title, content, and hints with unified vertical spacing."""
        sections = [
            section
            for section in (
                self.render_banner(color=color),
                self.render_title(color=color),
                '\n'.join(self.render_content(color=color)),
                self.render_hints(),
            )
            if section
        ]
        output = '\n\n'.join(sections)
        return with_border(output) if self.bordered else output

    def handle_mouse(self, mouse_event: MouseEvent) -> bool:
        """Optional hook for screens that handle mouse input."""
        return False

    def __str__(self) -> str:
        return self.render(color=False)


SelectHandler = Callable[[ScreenItem], None]


class SelectableScreen(Screen):
    """Screen with vertical cursor navigation over a list of items."""

    items: Sequence[ScreenItem] = ()
    selected_idx: int = 0

    def __init__(
        self,
        items: Sequence[ScreenItem] | None = None,
        on_select: SelectHandler | None = None,
        on_quit: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self.items = list(items or self.items)
        if not self.items:
            raise ValueError('A selectable screen requires at least one item.')
        self.selected_idx %= len(self.items)
        self._on_select = on_select
        self._on_quit = on_quit
        self._setup_keybindings()

    def _setup_keybindings(self) -> None:
        @self.kb.add('up')
        def _(event):
            self.select_prev()

        @self.kb.add('down')
        def _(event):
            self.select_next()

        @self.kb.add('enter')
        def _(event):
            self.on_select(self.get_selected_item())

        for item in self.items:
            keys = {item.key, item.key.swapcase()} if item.key.isalpha() else {item.key}
            for k in keys:

                @self.kb.add(k)
                def _(event, it=item):
                    self.on_select(it)

    def on_select(self, item: ScreenItem) -> None:
        """Override in subclasses or supply a callback to handle item selection."""
        if self._on_select:
            self._on_select(item)

    def select_next(self) -> None:
        """Move selection cursor down."""
        self.selected_idx = (self.selected_idx + 1) % len(self.items)

    def select_prev(self) -> None:
        """Move selection cursor up."""
        self.selected_idx = (self.selected_idx - 1) % len(self.items)

    def get_selected_item(self) -> ScreenItem:
        """Return the currently selected item."""
        return self.items[self.selected_idx]

    def format_item(self, item: ScreenItem) -> str:
        """Format an individual item for display."""
        return f'[{item.key}] {item.label}'

    def cancel(self) -> None:
        """Hook for screens that support cancellation (e.g., Esc)."""

    def quit(self) -> None:
        """Hook for screens that support quitting (e.g., q)."""
        if self._on_quit:
            self._on_quit()

    def handle_mouse(self, mouse_event: MouseEvent) -> bool:
        return handle_menu_mouse(self, mouse_event)

    def render_content(self, color: bool = True) -> list[str]:
        """Render selectable item lines with cursor markers and selection highlight."""
        lines: list[str] = []
        for idx, item in enumerate(self.items):
            is_selected = idx == self.selected_idx
            marker = '>' if is_selected else ' '
            marker_end = '<' if is_selected else ' '
            line_text = f'{marker} {self.format_item(item)} {marker_end}'
            if color and is_selected:
                line_text = colored(line_text, 'green', attrs=['bold'])
            else:
                line_text = colorize_suits(line_text, color=color)
            lines.append(center_line(line_text))
        return lines
