from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.mouse_events import MouseEvent

from core.board import Board
from core.mouse import BoardMouseController


class Game:
    """Generic base class for terminal card games."""

    def __init__(self, board: Board):
        self.board = board
        self.mouse = self.create_mouse_controller()
        self.kb = KeyBindings()
        self._setup_default_keybindings()
        self.setup_keybindings()

    def create_mouse_controller(self) -> BoardMouseController:
        """Create mouse controller for this game. Override in subclasses."""
        return BoardMouseController(self.board)

    def is_won(self) -> bool:
        """True if the game's win condition is satisfied."""
        return self.board.is_won()

    def restart(self):
        """Reset the board for a new game."""
        self.board.reset()
        self.mouse.reset()

    # --- default key bindings ---

    def _setup_default_keybindings(self):
        for direction in ('up', 'down', 'left', 'right'):

            @self.kb.add(direction)
            def _(event, d=direction):
                self.board.navigate_board(d)

    def setup_keybindings(self):
        """Hook for subclasses to register game-specific key bindings."""

    def render(self, color: bool = True) -> str:
        """Render the game board to string."""
        grid = self.board.get_print_string()
        return '\n'.join(''.join(row) for row in grid)

    def handle_mouse(self, mouse_event: MouseEvent) -> bool:
        """Delegate mouse event to the mouse controller."""
        return self.mouse.handle_mouse(mouse_event)
