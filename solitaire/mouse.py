from core.mouse import BoardMouseController, GridHit
from solitaire.board import Board
from solitaire.pile import SolitairePile


class SolitaireMouseController(BoardMouseController):
    """Minimal mouse controller for Klondike Solitaire."""

    board: Board

    def on_double_click(self, hit: GridHit) -> bool:
        pile = self.board.board[hit.row][hit.col]
        if hit.card_idx is not None and hit.card_idx != len(pile) - 1:
            return False
        if self.board.auto_move_to_foundation(pile):
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
        pile = self.board.board[hit.row][hit.col]
        depth = pile.get_depth_at_index(hit.card_idx) if pile in self.board.tableau else None

        # 1. clicking the already-selected source pile adjusts depth or deselects
        if pile == self.board.from_pile:
            if depth is not None and depth != pile.select_count:
                pile.set_select_count(depth)
            else:
                self.board.deselect_from_pile()
            return True

        # 2. clicking a valid destination pile executes the move
        if self.board.can_move_to(pile):
            self.board.navigate_to_coordinate(hit.row, hit.col)
            self.board.choose_pile()
            return True

        # 3. otherwise clear previous selection and act on the clicked pile if is clickable
        had_selection = self.board.from_pile is not None
        self.board.deselect_from_pile()

        if not self._is_clickable(pile, hit.card_idx):
            return had_selection

        self.board.navigate_to_coordinate(hit.row, hit.col)
        self.board.choose_pile()
        if pile == self.board.from_pile and depth is not None:
            pile.set_select_count(depth)
        return True

    def _is_clickable(self, pile: SolitairePile, card_idx: int | None) -> bool:
        if pile == self.board.stock_pile:
            return not (pile.is_empty() and self.board.waste_pile.is_empty())
        if pile.is_empty():
            return False
        if pile in self.board.tableau and card_idx is not None and card_idx < len(pile) - 1:
            return pile.cards[card_idx].face_up
        return True
