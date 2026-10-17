from core.board import Board as BaseBoard
from core.card import Card, Rank, Suit
from core.pile import Pile
from solitaire.pile import SolitairePile


class Board(BaseBoard):
    """Solitaire board implementation."""

    def reset(self):
        """Reset the Solitaire board to a newly dealt game."""
        all_cards: list[Card] = [Card(rank, suit) for suit in Suit for rank in Rank]
        self.stock_pile = SolitairePile(all_cards)
        self.stock_pile.shuffle()

        self.tableau: list[SolitairePile] = [SolitairePile([], stretched=True) for _ in range(7)]
        self.foundations: list[SolitairePile] = [SolitairePile([]) for _ in range(4)]
        self.waste_pile = SolitairePile([])

        self.from_pile: SolitairePile | None = None

        self.board: list[list[SolitairePile]] = [
            [*self.foundations, SolitairePile(None), self.waste_pile, self.stock_pile],
            [*self.tableau],
        ]

        self.deal_cards_to_tableau()

        self.current_selection = (0, 6)
        self.current_pile.select()

    # --- setup ---

    def deal_cards_to_tableau(self):
        """Deal cards into the 7 tableau columns with top card face-up."""
        for i, pile in enumerate(self.tableau):
            for j in range(i + 1):
                self.stock_pile.move_top_card_to_pile(pile, face_up=(j == i))

    # --- selection count ---

    def increase_select_count(self):
        pile = self.from_pile or self.current_pile
        if pile in self.tableau:
            pile.increase_select_count()

    def decrease_select_count(self):
        pile = self.from_pile or self.current_pile
        if pile in self.tableau:
            pile.decrease_select_count()

    def is_won(self) -> bool:
        """True if all 4 foundations are valid and complete (13 cards, Ace to King, all 4 suits)."""
        return (
            len(self.foundations) == 4
            and all(f.is_complete_foundation() for f in self.foundations)
            and {f.cards[0].suit for f in self.foundations} == set(Suit)
        )

    # --- game logic ---

    def can_move_to(self, to_pile: SolitairePile) -> bool:
        """True if the currently chosen from_pile can legally move to to_pile."""
        if self.from_pile is None or to_pile.is_top_card_face_down():
            return False
        return (to_pile in self.foundations and self.from_pile.is_valid_foundation_move(to_pile)) or (
            to_pile in self.tableau and self.from_pile.is_valid_tableau_move(to_pile)
        )

    def _execute_move(self, from_pile: SolitairePile, to_pile: SolitairePile):
        """Move selected cards, flip newly exposed top card, and restore cursor."""
        from_pile.move_selected_cards_to_pile(to_pile)
        if not from_pile.is_empty():
            from_pile.show_top_card()
        self.from_pile = from_pile
        self.deselect_from_pile()

    def auto_move_to_foundation(self, pile: SolitairePile | None = None) -> bool:
        """Attempt to move the top card of `pile` (default: current_pile) to an eligible foundation."""
        source = pile or self.current_pile
        if source not in (*self.tableau, self.waste_pile) or source.is_empty() or source.is_top_card_face_down():
            return False

        card = source.get_top_card()
        target = next((f for f in self.foundations if f.can_accept_foundation_card(card)), None)
        if target is None:
            return False

        self.deselect_from_pile()
        source.set_select_count(1)
        self._execute_move(source, target)
        return True

    def choose_pile(self):
        """Handle selecting, deselecting, and moving cards between piles."""
        to_pile = self.current_pile

        if to_pile == self.stock_pile:
            self.deselect_from_pile()
            if self.stock_pile.is_empty():
                self.waste_pile.move_to_pile(self.stock_pile, face_up=False)
            else:
                self.stock_pile.move_top_card_to_pile(self.waste_pile, face_up=True)
            self.stock_pile.reset_select_count()
            return

        if to_pile.is_top_card_face_down():
            self.deselect_from_pile()
            to_pile.show_top_card()
            to_pile.reset_select_count()
            return

        if self.from_pile == to_pile:
            self.deselect_from_pile()
            return

        if self.from_pile is None:
            if not to_pile.is_empty():
                if not to_pile.is_selected:
                    to_pile.select()
                self.from_pile = to_pile
            return

        if self.can_move_to(to_pile):
            self._execute_move(self.from_pile, to_pile)

    # --- navigation & selection hooks ---

    def deselect_from_pile(self):
        if self.from_pile is None:
            return
        self.from_pile.deselect()
        self.from_pile = None
        self.current_pile.select()

    def _on_leave(self, row: int, col: int):
        pile = self.board[row][col]
        if self.from_pile != pile:
            pile.deselect()

    def _on_enter(self, row: int, col: int):
        self.board[row][col].select()

    def _pile_indicator(self, pile: Pile) -> tuple[str, str | None] | None:
        is_chosen = self.from_pile == pile
        if pile.is_selected or is_chosen:
            color = 'yellow' if (pile.is_selected and is_chosen) else ('red' if is_chosen else None)
            return (self.INDICATOR, color)
        return None
