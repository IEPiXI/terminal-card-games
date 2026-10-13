import unittest

from core.card import Card, Rank, Suit
from solitaire.pile import SolitairePile


def full_foundation(suit: Suit = Suit.SPADE) -> list[Card]:
    """Create a complete Ace-to-King card list for a suit."""
    return [Card(Rank(val), suit, face_up=True) for val in range(1, 14)]


class TestSolitairePile(unittest.TestCase):
    def test_selection_lifecycle(self):
        card = Card(Rank.ACE, Suit.SPADE, face_up=True)
        pile = SolitairePile([card])

        self.assertFalse(pile.is_selected)
        self.assertEqual(pile.select_count, 0)
        self.assertEqual(pile.selected_cards, [])

        pile.select()
        self.assertTrue(pile.is_selected)
        self.assertEqual(pile.select_count, 1)
        self.assertEqual(pile.selected_cards, [card])

        pile.deselect()
        self.assertFalse(pile.is_selected)
        self.assertEqual(pile.select_count, 0)
        self.assertEqual(pile.selected_cards, [])

        empty = SolitairePile([])
        empty.select()
        self.assertTrue(empty.is_selected)
        self.assertEqual(empty.select_count, 0)
        self.assertEqual(empty.selected_cards, [])

    def test_multi_card_selection_bounds(self):
        c_down = Card(Rank.TWO, Suit.CLUB, face_up=False)
        c_up1 = Card(Rank.EIGHT, Suit.CLUB, face_up=True)
        c_up2 = Card(Rank.SEVEN, Suit.HEART, face_up=True)
        c_up3 = Card(Rank.SIX, Suit.SPADE, face_up=True)

        pile = SolitairePile([c_down, c_up1, c_up2, c_up3])
        pile.select()
        self.assertEqual(pile.selected_cards, [c_up3])

        # decreasing from 1 wraps to all visible face-up cards (3)
        pile.decrease_select_count()
        self.assertEqual(pile.select_count, 3)
        self.assertEqual(pile.selected_cards, [c_up3, c_up2, c_up1])

        # decreasing from 3 steps to 2
        pile.decrease_select_count()
        self.assertEqual(pile.select_count, 2)
        self.assertEqual(pile.selected_cards, [c_up3, c_up2])

        # increasing from 2 steps to 3
        pile.increase_select_count()
        self.assertEqual(pile.select_count, 3)

        # increasing from 3 wraps back to 1
        pile.increase_select_count()
        self.assertEqual(pile.select_count, 1)
        self.assertEqual(pile.selected_cards, [c_up3])

        # face-down-only pile cannot select cards
        down_only = SolitairePile([c_down])
        down_only.select()
        down_only.increase_select_count()
        self.assertEqual(down_only.selected_cards, [])
        down_only.decrease_select_count()
        self.assertEqual(down_only.selected_cards, [])

    def test_tableau_move_validation(self):
        c7_spade = Card(Rank.SEVEN, Suit.SPADE, face_up=True)
        src = SolitairePile([c7_spade])
        src.select()

        # valid: alternating color, descending rank
        self.assertTrue(src.is_valid_tableau_move(SolitairePile([Card(Rank.EIGHT, Suit.HEART, face_up=True)])))

        # invalid: same color or wrong rank
        self.assertFalse(src.is_valid_tableau_move(SolitairePile([Card(Rank.EIGHT, Suit.CLUB, face_up=True)])))
        self.assertFalse(src.is_valid_tableau_move(SolitairePile([Card(Rank.NINE, Suit.HEART, face_up=True)])))
        self.assertFalse(src.is_valid_tableau_move(SolitairePile([Card(Rank.SEVEN, Suit.HEART, face_up=True)])))
        self.assertFalse(src.is_valid_tableau_move(SolitairePile([Card(Rank.SIX, Suit.HEART, face_up=True)])))

        # invalid: unselected source
        unselected = SolitairePile([c7_spade])
        self.assertFalse(unselected.is_valid_tableau_move(SolitairePile([Card(Rank.EIGHT, Suit.HEART, face_up=True)])))

    def test_tableau_move_to_empty_and_multi_card(self):
        empty = SolitairePile([])

        king_pile = SolitairePile([Card(Rank.KING, Suit.SPADE, face_up=True)])
        king_pile.select()
        self.assertTrue(king_pile.is_valid_tableau_move(empty))

        queen_pile = SolitairePile([Card(Rank.QUEEN, Suit.HEART, face_up=True)])
        queen_pile.select()
        self.assertFalse(queen_pile.is_valid_tableau_move(empty))

        # multi-card run validates using the base card of the selected stack
        k_diamond = Card(Rank.KING, Suit.DIAMOND, face_up=True)
        q_club = Card(Rank.QUEEN, Suit.CLUB, face_up=True)
        j_heart = Card(Rank.JACK, Suit.HEART, face_up=True)
        stack = SolitairePile([k_diamond, q_club, j_heart])
        stack.select()
        stack.increase_select_count()  # selects [j_heart, q_club] (base is q_club)

        self.assertTrue(stack.is_valid_tableau_move(SolitairePile([Card(Rank.KING, Suit.HEART, face_up=True)])))
        self.assertFalse(stack.is_valid_tableau_move(SolitairePile([Card(Rank.KING, Suit.SPADE, face_up=True)])))
        self.assertFalse(stack.is_valid_tableau_move(empty))

        stack.increase_select_count()  # selects all 3 (base is k_diamond)
        self.assertTrue(stack.is_valid_tableau_move(empty))

    def test_foundation_move_validation(self):
        empty_foundation = SolitairePile([])
        ace_heart = Card(Rank.ACE, Suit.HEART, face_up=True)
        two_heart = Card(Rank.TWO, Suit.HEART, face_up=True)
        two_spade = Card(Rank.TWO, Suit.SPADE, face_up=True)

        src_ace = SolitairePile([ace_heart])
        src_ace.select()
        self.assertTrue(src_ace.is_valid_foundation_move(empty_foundation))

        src_two = SolitairePile([two_heart])
        src_two.select()
        self.assertFalse(src_two.is_valid_foundation_move(empty_foundation))

        foundation = SolitairePile([ace_heart])
        self.assertTrue(src_two.is_valid_foundation_move(foundation))

        src_spade = SolitairePile([two_spade])
        src_spade.select()
        self.assertFalse(src_spade.is_valid_foundation_move(foundation))

        # multi-card move to foundation is rejected
        multi = SolitairePile([two_heart, Card(Rank.THREE, Suit.HEART, face_up=True)])
        multi.select()
        multi.increase_select_count()
        self.assertFalse(multi.is_valid_foundation_move(foundation))

    def test_is_complete_foundation(self):
        pile = SolitairePile([])
        self.assertFalse(pile.is_complete_foundation())

        pile.cards = full_foundation()[:12]
        self.assertFalse(pile.is_complete_foundation())

        pile.cards = full_foundation()
        self.assertTrue(pile.is_complete_foundation())

        pile.cards.append(Card(Rank.ACE, Suit.SPADE, face_up=True))
        self.assertFalse(pile.is_complete_foundation())

    def test_move_selected_cards_to_pile(self):
        c_base = Card(Rank.EIGHT, Suit.CLUB, face_up=True)
        c_mid = Card(Rank.SEVEN, Suit.HEART, face_up=True)
        c_top = Card(Rank.SIX, Suit.SPADE, face_up=True)
        c_target = Card(Rank.NINE, Suit.DIAMOND, face_up=True)

        src = SolitairePile([c_base, c_mid, c_top])
        dst = SolitairePile([c_target])
        src.select()
        src.increase_select_count()
        src.increase_select_count()

        src.move_selected_cards_to_pile(dst)
        self.assertTrue(src.is_empty())
        self.assertEqual(src.select_count, 0)
        self.assertEqual(dst.cards, [c_target, c_base, c_mid, c_top])
