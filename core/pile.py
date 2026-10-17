from __future__ import annotations

import random

from termcolor import colored

from core.card import Card


class Pile:
    """
    Generic pile of cards usable across card games.

    Use cards=None for a visual spacer (is_none() returns True).
    Use cards=[] for an empty but interactive pile.
    """

    WIDTH: int = 6
    HEIGHT: int = 5
    OVERLAP: int = 2

    def __init__(self, cards: list[Card] | None = None, stretched: bool = False):
        self.cards = cards  # none is intentional: marks a non-interactive spacer
        self.stretched = stretched

    def __len__(self) -> int:
        """Return the number of cards in the pile."""
        return len(self.cards) if self.cards is not None else 0

    def is_none(self) -> bool:
        """True for non-interactive spacer piles (cards is None)."""
        return self.cards is None

    def is_empty(self) -> bool:
        """True if the pile contains no cards."""
        return not self.cards

    def is_only_one(self) -> bool:
        """True if the pile contains exactly one card."""
        return len(self) == 1

    def get_top_card(self) -> Card | None:
        """Return the top card of the pile, or None if empty."""
        return self.cards[-1] if self.cards else None

    def is_top_card_face_down(self) -> bool:
        """True if the top card exists and is face-down."""
        card = self.get_top_card()
        return bool(card and not card.face_up)

    def show_top_card(self):
        """Flip the top card face-up if present."""
        card = self.get_top_card()
        if card:
            card.face_up = True

    def get_visible_cards(self) -> list[Card]:
        """Return the contiguous run of face-up cards from the top."""
        visible = []
        if self.is_empty():
            return visible
        for card in reversed(self.cards):
            if not card.face_up:
                break
            visible.append(card)
        return visible

    def get_height(self, stretched: bool | None = None) -> int:
        """Return rendered height of this pile in lines."""
        is_stretched = self.stretched if stretched is None else stretched
        if self.is_none() or self.is_empty() or not is_stretched:
            return self.HEIGHT
        return (len(self.cards) - 1) * self.OVERLAP + self.HEIGHT

    def get_card_at_offset(self, y_offset: int) -> int | None:
        """Return index of the card located at vertical line y_offset within this pile."""
        if y_offset < 0 or self.is_empty():
            return None
        top_idx = len(self.cards) - 1
        top_card_y = top_idx * self.OVERLAP
        if y_offset < top_card_y:
            return y_offset // self.OVERLAP
        if y_offset < top_card_y + self.HEIGHT:
            return top_idx
        return None

    # --- card actions ---

    def shuffle(self):
        """Randomly reorder the cards in this pile."""
        random.shuffle(self.cards)

    def move_card_to_pile(self, card: Card, pile: Pile, face_up: bool = True):
        """Move a specific card from this pile to the top of another pile."""
        card.face_up = face_up
        pile.cards.append(card)
        self.cards.remove(card)

    def move_top_card_to_pile(self, pile: Pile, face_up: bool = True):
        """Move the top card from this pile to another pile."""
        if card := self.get_top_card():
            self.move_card_to_pile(card, pile, face_up)

    def move_to_pile(self, pile: Pile, face_up: bool = False):
        """Move all cards from this pile into another in reverse order."""
        if self.is_empty():
            return
        pile.cards.extend(reversed(self.cards))
        for card in pile.cards:
            card.face_up = face_up
        self.cards.clear()

    # --- rendering ---

    def get_print_string(
        self, stretched: bool | None = None, highlighted_cards: list[Card] | None = None
    ) -> list[list[str]]:
        """
        Render the pile as a grid of terminal strings.

        Args:
            stretched: Show every card individually (stretched out to the bottom).
            highlighted_cards: Cards to render with a highlighted red border.
        """
        is_stretched = self.stretched if stretched is None else stretched
        highlighted = highlighted_cards or []

        def _hl(card: Card) -> bool:
            return card in highlighted

        def _color(s: str, highlight: bool) -> str:
            return colored(s, 'red') if highlight else s

        if self.is_none():
            return [[' ' * self.WIDTH] for _ in range(self.HEIGHT)]

        if self.is_empty():
            return [[' ____ '], ['|    |'], ['|    |'], ['|    |'], [' ¯¯¯¯ ']]

        result = []

        if is_stretched:
            result.append([_color(' ____ ', _hl(self.cards[0]))])

            for i, card in enumerate(self.cards[:-1]):
                side = _color('|', _hl(card))
                result.append([f'{side}{card.get_print_string(0)}{side}'])
                result.append([f'{side}{_color("____", _hl(self.cards[i + 1]))}{side}'])

            top = self.get_top_card()
            side = _color('|', _hl(top))
            for i in range(3):
                result.append([f'{side}{top.get_print_string(i)}{side}'])
            result.append([_color(' ¯¯¯¯ ', _hl(top))])

        else:
            single = self.is_only_one()
            top = self.get_top_card()
            side = _color('|' if single else '‖', _hl(top))
            result.append([_color(' ____ ' if single else ' ‗‗‗‗ ', _hl(top))])
            for i in range(3):
                result.append([f'{_color("|", _hl(top))}{top.get_print_string(i)}{side}'])
            result.append([_color(' ¯¯¯¯ ', _hl(top))])

        return result
