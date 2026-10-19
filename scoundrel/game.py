from core.game import Game
from scoundrel.board import Board
from scoundrel.mouse import ScoundrelMouseController


class ScoundrelGame(Game):
    """Scoundrel rogue-like terminal card game."""

    def __init__(self):
        super().__init__(Board())

    def create_mouse_controller(self) -> ScoundrelMouseController:
        return ScoundrelMouseController(self.board)

    def setup_keybindings(self):
        @self.kb.add('enter')
        @self.kb.add('space')
        def _(event):
            if self.board.from_pile is not None and self.board.current_pile != self.board.from_pile:
                self.board.choose_pile()
            elif self.board.current_pile in self.board.room:
                self.board.auto_resolve_card()
            elif self.board.current_pile == self.board.dungeon_pile:
                self.board.avoid_room()
            else:
                self.board.choose_pile()

        @self.kb.add('escape')
        def _(event):
            self.board.deselect_from_pile()

        @self.kb.add('f')
        @self.kb.add('a')
        def _(event):
            self.board.auto_resolve_card()

        @self.kb.add('w')
        def _(event):
            self.board.act_with_weapon()

        @self.kb.add('b')
        def _(event):
            self.board.act_barehanded()

        @self.kb.add('p')
        @self.kb.add('h')
        def _(event):
            self.board.act_potion()

        @self.kb.add('v')
        def _(event):
            self.board.avoid_room()

        # jump directly to room cards 1..4
        for idx in range(Board.ROOM_SIZE):

            @self.kb.add(str(idx + 1))
            def _(event, c=Board.ROOM_START_COL + idx):
                self.board.navigate_to_coordinate(0, c)

        # jump directly to dungeon, weapon, and discard piles
        jump_map = {
            '0': (0, Board.DUNGEON_COL),
            'd': (0, Board.DUNGEON_COL),
            '^': (0, Board.DUNGEON_COL),
            '5': (1, Board.WEAPON_COL),
            'e': (1, Board.WEAPON_COL),
            '6': (0, Board.DISCARD_COL),
            'x': (0, Board.DISCARD_COL),
        }
        for key, (r, c) in jump_map.items():

            @self.kb.add(key)
            def _(event, row=r, col=c):
                self.board.navigate_to_coordinate(row, col)
