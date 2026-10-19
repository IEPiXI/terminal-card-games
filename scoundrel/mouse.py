from core.mouse import BoardMouseController, GridHit
from scoundrel.board import Board
from scoundrel.pile import ScoundrelPile


class ScoundrelMouseController(BoardMouseController):
    """Mouse controller for Scoundrel."""

    board: Board

    def on_double_click(self, hit: GridHit) -> bool:
        if self.board.is_game_over():
            return False
        pile = self.board.board[hit.row][hit.col]
        if pile in self.board.room and not pile.is_empty():
            if self.board.auto_resolve_card(pile):
                self.board.navigate_to_coordinate(hit.row, hit.col)
                self.board.current_pile.deselect()
                return True
        return False

    def on_click(self, hit: GridHit) -> bool:
        handled = self._handle_click(hit)
        if self.board.from_pile is None:
            self.board.current_pile.deselect()
        return handled

    def _handle_click(self, hit: GridHit) -> bool:
        if self.board.is_game_over():
            return False
        pile = self.board.board[hit.row][hit.col]

        # 1. clicking the already-selected room pile deselects it
        if pile == self.board.from_pile:
            self.board.deselect_from_pile()
            return True

        # 2. clicking a valid target pile (weapon or discard) executes the move
        if self.board.can_move_to(pile):
            self.board.navigate_to_coordinate(hit.row, hit.col)
            self.board.choose_pile()
            return True

        # 3. otherwise clear previous selection and act on the clicked pile if clickable
        had_selection = self.board.from_pile is not None
        self.board.deselect_from_pile()
        if not self._is_clickable(pile):
            return had_selection

        self.board.navigate_to_coordinate(hit.row, hit.col)
        self.board.choose_pile()
        return True

    def _is_clickable(self, pile: ScoundrelPile) -> bool:
        if pile == self.board.dungeon_pile:
            return self.board.can_avoid_room()
        if pile in self.board.room:
            return not pile.is_empty()
        return False
