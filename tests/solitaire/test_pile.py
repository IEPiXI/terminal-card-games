import unittest

from core.card import Card, Rank, Suit
from solitaire.pile import SolitairePile


def full_foundation(suit: Suit = Suit.SPADE) -> list[Card]:
    """Create a complete Ace-to-King card list for a suit."""
    return [Card(Rank(val), suit, face_up=True) for val in range(1, 14)]


class TestSolitairePile(unittest.TestCase):
    def setUp(self):
        self.c_down = Card(Rank.TWO, Suit.CLUB, face_up=False)
        self.c8_club = Card(Rank.EIGHT, Suit.CLUB, face_up=True)
        self.c7_heart = Card(Rank.SEVEN, Suit.HEART, face_up=True)
        self.c6_spade = Card(Rank.SIX, Suit.SPADE, face_up=True)
        # standard cascade: 1 face-down card + 3 face-up cards (top card is 6♠)
        self.cascade = SolitairePile([self.c_down, self.c8_club, self.c7_heart, self.c6_spade])

    def test_selection_lifecycle(self):
        pile = SolitairePile([self.c6_spade])
        self.assertFalse(pile.is_selected)
        self.assertEqual(pile.selected_cards, [])

        pile.select()
        self.assertTrue(pile.is_selected)
        self.assertEqual(pile.selected_cards, [self.c6_spade])

        pile.deselect()
        self.assertFalse(pile.is_selected)
        self.assertEqual(pile.selected_cards, [])

        empty = SolitairePile([])
        empty.select()
        self.assertTrue(empty.is_selected)
        self.assertEqual(empty.selected_cards, [])

    def test_multi_card_selection_wrapping(self):
        self.cascade.select()
        self.assertEqual(self.cascade.selected_cards, [self.c6_spade])

        # decreasing from 1 wraps to all 3 visible face-up cards (ignoring c_down)
        self.cascade.decrease_select_count()
        self.assertEqual(self.cascade.selected_cards, [self.c6_spade, self.c7_heart, self.c8_club])

        self.cascade.decrease_select_count()
        self.assertEqual(self.cascade.selected_cards, [self.c6_spade, self.c7_heart])

        self.cascade.increase_select_count()
        self.assertEqual(self.cascade.select_count, 3)

        # increasing from max visible wraps back to 1
        self.cascade.increase_select_count()
        self.assertEqual(self.cascade.selected_cards, [self.c6_spade])

        # face-down-only pile cannot select any cards
        down_only = SolitairePile([self.c_down])
        down_only.select()
        down_only.increase_select_count()
        self.assertEqual(down_only.selected_cards, [])

    def test_set_select_count_and_depth_at_index(self):
        self.assertIsNone(self.cascade.get_depth_at_index(None))
        self.assertIsNone(self.cascade.get_depth_at_index(0))  # face-down
        self.assertEqual(self.cascade.get_depth_at_index(1), 3)  # c8_club
        self.assertEqual(self.cascade.get_depth_at_index(3), 1)  # c6_spade (top)

        self.assertTrue(self.cascade.set_select_count(2))
        self.assertEqual(self.cascade.selected_cards, [self.c6_spade, self.c7_heart])
        self.assertFalse(self.cascade.set_select_count(4))

    def test_tableau_move_validation(self):
        empty = SolitairePile([])
        target_8h = SolitairePile([Card(Rank.EIGHT, Suit.HEART, face_up=True)])
        target_8c = SolitairePile([self.c8_club])
        target_9d = SolitairePile([Card(Rank.NINE, Suit.DIAMOND, face_up=True)])

        self.assertFalse(target_8h.can_accept_tableau_card(None))
        self.assertFalse(self.cascade.is_valid_tableau_move(target_8h))  # unselected

        # select [6♠, 7♥] -> base card of moved run is 7♥
        self.cascade.set_select_count(2)
        self.assertTrue(self.cascade.is_valid_tableau_move(target_8c))  # 7♥ onto 8♣
        self.assertFalse(self.cascade.is_valid_tableau_move(target_8h))  # same color
        self.assertFalse(self.cascade.is_valid_tableau_move(target_9d))  # wrong rank
        self.assertFalse(self.cascade.is_valid_tableau_move(empty))  # non-King onto empty

        # only a King-base run can move to an empty tableau pile
        king_pile = SolitairePile([Card(Rank.KING, Suit.SPADE, face_up=True)])
        king_pile.select()
        self.assertTrue(king_pile.is_valid_tableau_move(empty))

    def test_foundation_move_validation(self):
        empty = SolitairePile([])
        ace_h = Card(Rank.ACE, Suit.HEART, face_up=True)
        two_h = Card(Rank.TWO, Suit.HEART, face_up=True)
        two_s = Card(Rank.TWO, Suit.SPADE, face_up=True)

        self.assertFalse(empty.can_accept_foundation_card(None))
        self.assertTrue(empty.can_accept_foundation_card(ace_h))
        self.assertFalse(empty.can_accept_foundation_card(two_h))

        foundation = SolitairePile([ace_h])
        src_two_h = SolitairePile([two_h])
        src_two_h.select()
        self.assertTrue(src_two_h.is_valid_foundation_move(foundation))

        src_two_s = SolitairePile([two_s])
        src_two_s.select()
        self.assertFalse(src_two_s.is_valid_foundation_move(foundation))  # wrong suit

        # multi-card selection cannot move to a foundation
        self.cascade.set_select_count(2)
        self.assertFalse(self.cascade.is_valid_foundation_move(foundation))

    def test_is_complete_foundation(self):
        pile = SolitairePile([])
        self.assertFalse(pile.is_complete_foundation())

        pile.cards = full_foundation()[:12]
        self.assertFalse(pile.is_complete_foundation())

        pile.cards = full_foundation()
        self.assertTrue(pile.is_complete_foundation())

        pile.cards.append(self.c6_spade)
        self.assertFalse(pile.is_complete_foundation())

    def test_move_selected_cards_to_pile(self):
        target_9d = Card(Rank.NINE, Suit.DIAMOND, face_up=True)
        dst = SolitairePile([target_9d])

        self.cascade.set_select_count(3)
        self.cascade.move_selected_cards_to_pile(dst)

        self.assertEqual(self.cascade.cards, [self.c_down])
        self.assertEqual(self.cascade.select_count, 0)
        self.assertEqual(dst.cards, [target_9d, self.c8_club, self.c7_heart, self.c6_spade])
