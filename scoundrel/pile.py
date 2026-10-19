from __future__ import annotations

from core.card import Card, Rank, Suit
from core.pile import Pile


def card_value(card: Card) -> int:
    """Return the Scoundrel numeric value of a card (2-10, J=11, Q=12, K=13, A=14)."""
    return 14 if card.rank == Rank.ACE else card.rank.value


def is_monster(card: Card | None) -> bool:
    """True if card is a Monster (Club or Spade)."""
    return card is not None and card.suit in (Suit.CLUB, Suit.SPADE)


def is_weapon(card: Card | None) -> bool:
    """True if card is a Weapon (Diamond)."""
    return card is not None and card.suit == Suit.DIAMOND


def is_potion(card: Card | None) -> bool:
    """True if card is a Health Potion (Heart)."""
    return card is not None and card.suit == Suit.HEART


class ScoundrelPile(Pile):
    """
    Pile subclass with Scoundrel-specific behaviour:
    - Single top-card selection highlighting
    - Staggered weapon + slain monster stack inspection
    - Bottom-of-dungeon placement when avoiding a room
    """

    def __init__(self, cards: list[Card] | None = None, stretched: bool = False):
        super().__init__(cards, stretched=stretched)
        self.is_selected: bool = False
        self.selected_cards: list[Card] = []

    # --- selection state ---

    def select(self):
        """Mark pile as selected and highlight top card if present."""
        self.is_selected = True
        self.reset_selection()

    def deselect(self):
        """Mark pile as unselected and clear highlighted cards."""
        self.is_selected = False
        self.reset_selection()

    def reset_selection(self):
        """Synchronize highlighted card list with current selection state."""
        if self.is_selected and not self.is_empty():
            self.selected_cards = [self.get_top_card()]
        else:
            self.selected_cards = []

    # --- weapon stack helpers ---

    def get_weapon_card(self) -> Card | None:
        """Return the base Diamond weapon card if equipped on this pile."""
        if not self.is_empty() and is_weapon(self.cards[0]):
            return self.cards[0]
        return None

    def get_slain_monsters(self) -> list[Card]:
        """Return all monsters currently stacked on top of the equipped weapon."""
        if self.get_weapon_card() is None:
            return []
        return [card for card in self.cards[1:] if is_monster(card)]

    def get_last_slain_monster(self) -> Card | None:
        """Return the most recently slain monster on this weapon, or None."""
        slain = self.get_slain_monsters()
        return slain[-1] if slain else None

    def get_weapon_value(self) -> int:
        """Return damage value of the equipped weapon, or 0 if unarmed."""
        weapon = self.get_weapon_card()
        return card_value(weapon) if weapon else 0

    def get_max_monster_value(self) -> int | None:
        """Return maximum monster value this weapon can slay, or None if unarmed."""
        if self.get_weapon_card() is None:
            return None
        last_monster = self.get_last_slain_monster()
        return card_value(last_monster) if last_monster is not None else 14

    def can_slay_monster(self, card: Card | None) -> bool:
        """True if this weapon pile has a weapon that can legally slay `card`."""
        if not is_monster(card):
            return False
        max_val = self.get_max_monster_value()
        return max_val is not None and card_value(card) <= max_val

    # --- card movement ---

    def move_top_card_to_bottom(self, pile: Pile, face_up: bool = False):
        """Move the top card of this pile to the bottom (index 0) of `pile`."""
        if card := self.get_top_card():
            card.face_up = face_up
            self.cards.remove(card)
            pile.cards.insert(0, card)

    # --- rendering ---

    def get_print_string(self, stretched: bool | None = None, **kwargs) -> list[list[str]]:
        """Delegate to generic Pile rendering with selected card highlighted."""
        return super().get_print_string(stretched=stretched, highlighted_cards=self.selected_cards)
