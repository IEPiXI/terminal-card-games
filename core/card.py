from __future__ import annotations

from enum import Enum

from termcolor import colored


class Suit(Enum):
    """Standard playing card suits."""

    CLUB = '♣'
    SPADE = '♠'
    DIAMOND = '♦'
    HEART = '♥'


suit_to_color = {
    Suit.CLUB: 'dark_grey',
    Suit.SPADE: 'dark_grey',
    Suit.DIAMOND: 'red',
    Suit.HEART: 'red',
}


class Rank(Enum):
    """Standard card ranks from Ace (1) to King (13)."""

    ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING = range(1, 14)

    def __str__(self) -> str:
        """Return the display character for the rank (e.g. 'A', '10', 'K')."""
        str_dict = {Rank.ACE: 'A', Rank.TEN: '10', Rank.JACK: 'J', Rank.QUEEN: 'Q', Rank.KING: 'K'}
        return str_dict.get(self, str(self.value))


class Card:
    """A single playing card with rank, suit, and face-up state."""

    def __init__(self, rank: Rank, suit: Suit, face_up: bool = False):
        self.rank = rank
        self.suit = suit
        self.face_up = face_up

    # --- relative comparisons ---

    def is_predecessor_of(self, other: Card | None) -> bool:
        """True if this card is one rank below other (Kings on empty)."""
        if other is None:
            return self.rank == Rank.KING
        return self.rank.value == other.rank.value - 1

    def is_successor_of(self, other: Card | None) -> bool:
        """True if this card is one rank above other (Aces on empty)."""
        if other is None:
            return self.rank == Rank.ACE
        return self.rank.value == other.rank.value + 1

    def is_opposite_color(self, other: Card | None) -> bool:
        """True if this card has a different color than other."""
        return other is None or suit_to_color[self.suit] != suit_to_color[other.suit]

    def is_same_suit(self, other: Card | None) -> bool:
        """True if this card shares the same suit with other."""
        return other is None or self.suit == other.suit

    # --- rendering ---

    def get_print_string(self, row: int) -> str:
        """Render row (0..2) of the card as a 4-character terminal string."""
        if not self.face_up:
            return colored('░░░░', 'light_blue')

        rank_str = str(self.rank)
        space = ' ' if len(rank_str) == 2 else '  '
        colored_suit = colored(self.suit.value, suit_to_color[self.suit])

        return {
            0: f'{colored_suit}{space}{rank_str}',
            1: '    ',
            2: f'{rank_str}{space}{colored_suit}',
        }[row]
