from core.game import Game
from solitaire.board import Board
from solitaire.mouse import SolitaireMouseController


class SolitaireGame(Game):
    """Solitaire terminal card game."""

    def __init__(self):
        super().__init__(Board())

    def create_mouse_controller(self) -> SolitaireMouseController:
        return SolitaireMouseController(self.board)

    def setup_keybindings(self):
        @self.kb.add('w')
        def _(event):
            self.board.increase_select_count()

        @self.kb.add('s')
        def _(event):
            self.board.decrease_select_count()

        @self.kb.add('enter')
        @self.kb.add('space')
        def _(event):
            self.board.choose_pile()

        @self.kb.add('escape')
        def _(event):
            self.board.deselect_from_pile()

        @self.kb.add('f')
        @self.kb.add('a')
        def _(event):
            self.board.auto_move_to_foundation()

        # jump directly to tableau columns (row 1, col 0..6)
        for col_idx in range(7):

            @self.kb.add(str(col_idx + 1))
            def _(event, c=col_idx):
                self.board.navigate_to_coordinate(1, c)

        # jump directly to top-row piles (row 0)
        top_row_map = {
            'c-1': (0, 0),
            'c-2': (0, 1),
            'c-3': (0, 2),
            'c-4': (0, 3),
            'c-5': (0, 5),
            'c-6': (0, 6),
            '!': (0, 0),
            '@': (0, 1),
            '"': (0, 1),
            '#': (0, 2),
            '§': (0, 2),
            '$': (0, 3),
            '%': (0, 5),
            '^': (0, 6),
            '&': (0, 6),
        }
        for key, (r, c) in top_row_map.items():

            @self.kb.add(key)
            def _(event, row=r, col=c):
                self.board.navigate_to_coordinate(row, col)
