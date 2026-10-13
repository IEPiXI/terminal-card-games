from __future__ import annotations

from core.card import Card
from core.pile import Pile


class SolitairePile(Pile):
    """
    Pile subclass with solitaire-specific behaviour:
    - Multi-card selection (select_count / selected_cards)
    - Tableau and foundation move validation
    - Terminal rendering with highlighted selected cards
    """

    def __init__(self, cards: list[Card] | None = None):
        super().__init__(cards)
        self.is_selected: bool = False
        self.select_count: int = 0
        self.selected_cards: list[Card] = []

    # --- selection state ---

    def select(self):
        """Mark pile as selected and select top card."""
        self.is_selected = True
        self.reset_select_count()

    def deselect(self):
        """Mark pile as unselected and clear selection."""
        self.is_selected = False
        self.reset_select_count()

    def update_select_count(self, delta: int):
        visible_cards = self.get_visible_cards()
        if not visible_cards:
            self.select_count = 0
            self.selected_cards = []
            return
        n = len(visible_cards)
        if self.select_count <= 0:
            self.select_count = 1 if delta > 0 else n
        else:
            self.select_count = (self.select_count + delta - 1) % n + 1
        self.selected_cards = visible_cards[: self.select_count]

    def increase_select_count(self):
        self.update_select_count(1)

    def decrease_select_count(self):
        self.update_select_count(-1)

    def reset_select_count(self):
        """Reset selection: top card if selected, otherwise empty."""
        if self.is_selected and not self.is_empty():
            self.select_count = 1
            self.selected_cards = [self.get_top_card()]
        else:
            self.select_count = 0
            self.selected_cards = []

    # --- move validation ---

    def is_valid_tableau_move(self, other: SolitairePile) -> bool:
        """Descending rank, alternating colour."""
        if not self.selected_cards:
            return False
        from_card = self.selected_cards[-1]
        to_card = other.get_top_card()
        return from_card.is_predecessor_of(to_card) and from_card.is_opposite_color(to_card)

    def is_valid_foundation_move(self, other: SolitairePile) -> bool:
        """Ascending rank, same suit, single card only."""
        if len(self.selected_cards) != 1:
            return False
        from_card = self.get_top_card()
        to_card = other.get_top_card()
        return from_card.is_successor_of(to_card) and from_card.is_same_suit(to_card)

    def is_complete_foundation(self) -> bool:
        """True if pile contains 13 cards of the same suit in ascending order (Ace to King)."""
        if len(self.cards) != 13:
            return False
        suit = self.cards[0].suit
        return all(card.suit == suit and card.rank.value == i + 1 for i, card in enumerate(self.cards))

    # --- card movement ---

    def move_selected_cards_to_pile(self, pile: SolitairePile):
        """Move selected cards to another pile and reset selection."""
        for card in self.selected_cards[::-1]:
            self.move_card_to_pile(card, pile, face_up=True)
        self.reset_select_count()

    # --- rendering ---

    def get_print_string(self, stretched: bool = False, **kwargs) -> list[list[str]]:
        """Delegate to generic Pile rendering, passing selected cards as highlighted."""
        return super().get_print_string(stretched=stretched, highlighted_cards=self.selected_cards)
