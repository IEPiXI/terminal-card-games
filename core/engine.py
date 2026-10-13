from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum, auto

from prompt_toolkit import Application
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import DynamicKeyBindings, KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl

from core.game import Game
from menu.base import Screen, ScreenItem
from menu.confirm_screen import ConfirmScreen
from menu.main_menu import TCGMenu
from menu.win_screen import WinScreen


class State(Enum):
    """Application runtime state."""

    MENU = auto()
    GAME = auto()


@dataclass(frozen=True)
class GameSpec:
    """Specification for a playable card game in the engine."""

    id: str
    title: str
    game_cls: type[Game]
    shortcut: str


class GameEngine:
    """Core terminal game engine managing state transitions and event loop."""

    def __init__(self, games: Sequence[GameSpec]):
        self.games: dict[str, GameSpec] = {g.id: g for g in games}
        self.state: State = State.MENU
        self.game: Game | None = None
        self.confirm_screen: ConfirmScreen | None = None

        menu_items = [ScreenItem(g.shortcut, g.title, g.id) for g in games]
        self.menu = TCGMenu(menu_items, on_select=self._on_menu_select)
        self.win_screen = WinScreen(on_select=self._on_win_select)

        self.kb = KeyBindings()
        self._setup_keybindings()

    @property
    def is_game(self) -> bool:
        return self.state == State.GAME and self.game is not None

    @property
    def is_won(self) -> bool:
        return self.is_game and self.game.is_won()

    @property
    def is_confirm(self) -> bool:
        return self.confirm_screen is not None

    @property
    def is_playing(self) -> bool:
        return self.is_game and not self.is_won and not self.is_confirm

    @property
    def active_view(self) -> Screen | Game:
        """Return the currently active screen or game instance."""
        if self.is_confirm:
            return self.confirm_screen
        if self.is_won:
            return self.win_screen
        if self.is_game:
            return self.game
        return self.menu

    def to_menu(self):
        """Switch to menu state."""
        self.state = State.MENU

    def to_game(self, game: Game):
        """Switch to active game state."""
        self.game = game
        self.state = State.GAME

    def start_game(self, game_id: str):
        """Launch the specified game."""
        if game_id in self.games:
            self.to_game(self.games[game_id].game_cls())

    def _on_menu_select(self, item: ScreenItem):
        self.start_game(item.value)

    def _on_win_select(self, item: ScreenItem):
        if item.value == 'restart' and self.game:
            self.game.restart()
        elif item.value == 'menu':
            self.to_menu()

    def confirm(self, message: str, action: Callable[[], None]):
        """Prompt user to confirm before running action."""

        def _resolve(confirmed: bool):
            self.confirm_screen = None
            if confirmed:
                action()

        self.confirm_screen = ConfirmScreen(message, on_close=_resolve)

    def _setup_keybindings(self):
        not_confirming = Condition(lambda: not self.is_confirm)
        is_playing = Condition(lambda: self.is_playing)

        @self.kb.add('c-c')
        def _(event):
            event.app.exit()

        @self.kb.add('q', filter=not_confirming)
        def _(event):
            self.confirm('Do you really want to quit?', event.app.exit)

        @self.kb.add('m', filter=is_playing)
        def _(event):
            self.confirm('Return to the main menu?', self.to_menu)

        @self.kb.add('r', filter=is_playing)
        def _(event):
            self.confirm('Reset the current game?', self.game.restart)

    def render(self, color: bool = True) -> str:
        """Render active screen depending on state."""
        return self.active_view.render(color=color)

    def run(self):
        """Run the unified prompt_toolkit application loop."""
        text_control = FormattedTextControl(
            text=lambda: ANSI(self.render()),
            focusable=False,
            show_cursor=False,
        )
        layout = Layout(Window(content=text_control))
        combined_kb = merge_key_bindings(
            [
                self.kb,
                DynamicKeyBindings(lambda: self.active_view.kb),
            ]
        )
        app = Application(
            layout=layout,
            key_bindings=combined_kb,
            full_screen=True,
            refresh_interval=0.1,
        )
        app.ttimeoutlen = 0.05
        app.run()
