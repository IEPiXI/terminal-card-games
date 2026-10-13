import unittest

from core.card import Card, Rank, Suit
from core.pile import Pile


class TestCard(unittest.TestCase):
    def test_properties(self):
        card = Card(Rank.ACE, Suit.SPADE, face_up=True)
        self.assertEqual(card.rank, Rank.ACE)
        self.assertEqual(card.suit, Suit.SPADE)
        self.assertTrue(card.face_up)

    def test_predecessor_logic(self):
        king = Card(Rank.KING, Suit.SPADE)
        queen = Card(Rank.QUEEN, Suit.HEART)
        jack = Card(Rank.JACK, Suit.CLUB)

        self.assertTrue(queen.is_predecessor_of(king))
        self.assertFalse(jack.is_predecessor_of(king))
        self.assertTrue(king.is_predecessor_of(None))
        self.assertFalse(queen.is_predecessor_of(None))

    def test_successor_logic(self):
        ace = Card(Rank.ACE, Suit.HEART)
        two = Card(Rank.TWO, Suit.HEART)
        three = Card(Rank.THREE, Suit.HEART)

        self.assertTrue(two.is_successor_of(ace))
        self.assertFalse(three.is_successor_of(ace))
        self.assertTrue(ace.is_successor_of(None))
        self.assertFalse(two.is_successor_of(None))

    def test_color_and_suit(self):
        spade = Card(Rank.FIVE, Suit.SPADE)
        club = Card(Rank.FIVE, Suit.CLUB)
        heart = Card(Rank.FIVE, Suit.HEART)
        diamond = Card(Rank.FIVE, Suit.DIAMOND)

        self.assertFalse(spade.is_opposite_color(club))
        self.assertTrue(spade.is_opposite_color(heart))
        self.assertTrue(spade.is_opposite_color(diamond))
        self.assertTrue(spade.is_same_suit(spade))
        self.assertFalse(spade.is_same_suit(heart))


class TestPile(unittest.TestCase):
    def setUp(self):
        self.ace_spades = Card(Rank.ACE, Suit.SPADE, face_up=True)
        self.two_spades = Card(Rank.TWO, Suit.SPADE, face_up=True)
        self.three_hearts = Card(Rank.THREE, Suit.HEART, face_up=False)

    def test_spacer_pile(self):
        spacer = Pile(None)
        self.assertTrue(spacer.is_none())
        self.assertTrue(spacer.is_empty())
        self.assertFalse(spacer.is_only_one())
        self.assertEqual(len(spacer), 0)
        self.assertIsNone(spacer.get_top_card())
        self.assertFalse(spacer.is_top_card_face_down())
        self.assertEqual(spacer.get_visible_cards(), [])

    def test_pile_sizes_and_top_card(self):
        empty = Pile([])
        self.assertFalse(empty.is_none())
        self.assertTrue(empty.is_empty())
        self.assertFalse(empty.is_only_one())
        self.assertEqual(len(empty), 0)
        self.assertIsNone(empty.get_top_card())

        single = Pile([self.ace_spades])
        self.assertFalse(single.is_empty())
        self.assertTrue(single.is_only_one())
        self.assertEqual(len(single), 1)
        self.assertEqual(single.get_top_card(), self.ace_spades)

        multi = Pile([self.ace_spades, self.two_spades, self.three_hearts])
        self.assertFalse(multi.is_empty())
        self.assertFalse(multi.is_only_one())
        self.assertEqual(len(multi), 3)
        self.assertEqual(multi.get_top_card(), self.three_hearts)

    def test_top_card_face_down_and_reveal(self):
        pile = Pile([self.three_hearts])
        self.assertTrue(pile.is_top_card_face_down())
        pile.show_top_card()
        self.assertFalse(pile.is_top_card_face_down())
        self.assertTrue(self.three_hearts.face_up)

        empty = Pile([])
        empty.show_top_card()
        self.assertFalse(empty.is_top_card_face_down())

    def test_get_visible_cards(self):
        self.assertEqual(Pile([]).get_visible_cards(), [])
        self.assertEqual(Pile([self.three_hearts]).get_visible_cards(), [])

        c_down = Card(Rank.FIVE, Suit.CLUB, face_up=False)
        c_up1 = Card(Rank.SEVEN, Suit.HEART, face_up=True)
        c_up2 = Card(Rank.EIGHT, Suit.SPADE, face_up=True)
        pile = Pile([c_down, c_up1, c_up2])
        self.assertEqual(pile.get_visible_cards(), [c_up2, c_up1])

    def test_move_card_to_pile(self):
        c1 = Card(Rank.ACE, Suit.SPADE, face_up=False)
        c2 = Card(Rank.TWO, Suit.SPADE, face_up=False)
        src = Pile([c1, c2])
        dst = Pile([])

        src.move_card_to_pile(c1, dst, face_up=True)
        self.assertEqual(src.cards, [c2])
        self.assertEqual(dst.cards, [c1])
        self.assertTrue(c1.face_up)

        src.move_card_to_pile(c2, dst, face_up=False)
        self.assertTrue(src.is_empty())
        self.assertEqual(dst.cards, [c1, c2])
        self.assertFalse(c2.face_up)

        with self.assertRaises(ValueError):
            src.move_card_to_pile(Card(Rank.KING, Suit.HEART), dst)

    def test_move_top_card_to_pile(self):
        c1 = Card(Rank.ACE, Suit.SPADE)
        c2 = Card(Rank.TWO, Suit.SPADE)
        src = Pile([c1, c2])
        dst = Pile([])

        src.move_top_card_to_pile(dst, face_up=True)
        self.assertEqual(src.cards, [c1])
        self.assertEqual(dst.cards, [c2])
        self.assertTrue(c2.face_up)

        src.move_top_card_to_pile(dst, face_up=True)
        self.assertTrue(src.is_empty())
        self.assertEqual(dst.cards, [c2, c1])

        # empty source is a safe no-op
        src.move_top_card_to_pile(dst)
        self.assertEqual(len(dst), 2)

    def test_move_to_pile(self):
        c_existing = Card(Rank.KING, Suit.DIAMOND, face_up=True)
        src = Pile([self.ace_spades, self.two_spades])
        dst = Pile([c_existing])

        src.move_to_pile(dst, face_up=False)
        self.assertTrue(src.is_empty())
        self.assertEqual(dst.cards, [c_existing, self.two_spades, self.ace_spades])
        self.assertTrue(all(not c.face_up for c in dst.cards))

        # empty source is a safe no-op
        src.move_to_pile(dst, face_up=True)
        self.assertEqual(len(dst), 3)

    def test_shuffle(self):
        cards = [Card(Rank(r), Suit.SPADE) for r in range(1, 14)]
        pile = Pile(list(cards))
        pile.shuffle()
        self.assertEqual(len(pile), 13)
        self.assertEqual(set(pile.cards), set(cards))

        single = Pile([self.ace_spades])
        single.shuffle()
        self.assertEqual(single.cards, [self.ace_spades])

        empty = Pile([])
        empty.shuffle()
        self.assertEqual(len(empty), 0)
