from termcolor import colored

from core.pile import Pile


class Board:
    """
    Generic grid-based card game board.

    Subclasses implement reset() to initialise self.board and
    self.current_selection, then override hooks for game-specific behaviour:
      - is_navigable    : which cells can be navigated to
      - _on_leave       : called when the cursor leaves a cell
      - _on_enter       : called when the cursor enters a cell
      - _pile_indicator : what indicator (if any) to draw beneath a pile
      - get_print_string: override for per-row stretch control
    """

    INDICATOR = '  /\\  '

    board: list[list[Pile]]
    current_selection: tuple[int, int]

    def __init__(self):
        self.reset()

    @property
    def current_pile(self) -> Pile:
        row, col = self.current_selection
        return self.board[row][col]

    def is_won(self) -> bool:
        """Return True if the board satisfies the win condition. Default is False."""
        return False

    def reset(self):
        """Reset the board to its initial state."""
        self.board = []
        self.current_selection = (0, 0)

    # --- navigation ---

    def _move_cursor(self, row: int, col: int):
        """Transition cursor to (row, col) if it is a new, navigable coordinate."""
        if (row, col) != self.current_selection and self.is_navigable(row, col):
            self._on_leave(*self.current_selection)
            self.current_selection = (row, col)
            self._on_enter(row, col)

    def navigate_board(self, direction: str):
        """Move the cursor one step, automatically skipping non-navigable cells."""
        deltas = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
        d_row, d_col = deltas.get(direction, (0, 0))

        def step(r: int, c: int) -> tuple[int, int]:
            r = (r + d_row) % len(self.board)
            c = (c + d_col) % len(self.board[r]) if d_col else min(c, len(self.board[r]) - 1)
            return r, c

        new = step(*self.current_selection)
        seen = {self.current_selection}
        while not self.is_navigable(*new) and new not in seen:
            seen.add(new)
            new = step(*new)

        self._move_cursor(*new)

    def navigate_to_coordinate(self, row: int, col: int):
        """Jump the cursor directly to a grid coordinate if navigable."""
        self._move_cursor(row, col)

    # --- hooks ---

    def is_navigable(self, row: int, col: int) -> bool:
        """Return False to skip this cell (e.g. visual spacers). Default: non-spacer cells are navigable."""
        if 0 <= row < len(self.board) and 0 <= col < len(self.board[row]):
            return not self.board[row][col].is_none()
        return False

    def _on_leave(self, row: int, col: int):
        """Called when the cursor leaves a cell. Override for deselect logic."""

    def _on_enter(self, row: int, col: int):
        """Called when the cursor enters a cell. Override for select logic."""

    def _pile_indicator(self, pile: Pile) -> tuple[str, str | None] | None:
        """
        Return (indicator_text, color_or_None) to show beneath a pile, or None.
        Default: show a plain arrow under the cursor pile only.
        """
        if pile is self.current_pile:
            return (self.INDICATOR, None)
        return None

    # --- rendering ---

    def _build_grid(self, piles: list[Pile], stretched: bool = False) -> list[list[str]]:
        """Build a 2D character grid for a row of piles, including indicators."""
        pile_strings = [p.get_print_string(stretched) for p in piles]
        max_height = max((len(p) for p in pile_strings), default=1)
        grid = [['      '] * len(piles) for _ in range(max_height + 1)]

        for col, (pile, lines) in enumerate(zip(piles, pile_strings)):
            for row_idx, line in enumerate(lines):
                grid[row_idx][col] = line[0]

            indicator = self._pile_indicator(pile)
            if indicator:
                text, color = indicator
                grid[len(lines)][col] = colored(text, color) if color else text

        return grid

    def get_print_string(self) -> list[list[str]]:
        """Render every board row unstretched. Override for per-row stretch control."""
        result = []
        for row in self.board:
            result.extend(self._build_grid(row))
        return result
