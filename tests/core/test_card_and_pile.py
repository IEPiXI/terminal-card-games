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
        self.ace = Card(Rank.ACE, Suit.SPADE, face_up=True)
        self.two = Card(Rank.TWO, Suit.SPADE, face_up=True)
        self.three_down = Card(Rank.THREE, Suit.HEART, face_up=False)

    def test_spacer_and_empty_states(self):
        spacer = Pile(None)
        self.assertTrue(spacer.is_none())
        self.assertTrue(spacer.is_empty())
        self.assertEqual(len(spacer), 0)
        self.assertIsNone(spacer.get_top_card())

        empty = Pile([])
        self.assertFalse(empty.is_none())
        self.assertTrue(empty.is_empty())
        self.assertFalse(empty.is_only_one())
        self.assertIsNone(empty.get_top_card())

    def test_populated_pile_queries(self):
        single = Pile([self.ace])
        self.assertTrue(single.is_only_one())
        self.assertEqual(single.get_top_card(), self.ace)

        multi = Pile([self.ace, self.two, self.three_down])
        self.assertFalse(multi.is_only_one())
        self.assertEqual(len(multi), 3)
        self.assertEqual(multi.get_top_card(), self.three_down)

    def test_top_card_face_down_and_reveal(self):
        pile = Pile([self.three_down])
        self.assertTrue(pile.is_top_card_face_down())
        pile.show_top_card()
        self.assertFalse(pile.is_top_card_face_down())
        self.assertTrue(self.three_down.face_up)

        empty = Pile([])
        empty.show_top_card()
        self.assertFalse(empty.is_top_card_face_down())

    def test_get_visible_cards(self):
        self.assertEqual(Pile([]).get_visible_cards(), [])
        self.assertEqual(Pile([self.three_down]).get_visible_cards(), [])

        pile = Pile([self.three_down, self.ace, self.two])
        self.assertEqual(pile.get_visible_cards(), [self.two, self.ace])

    def test_move_card_to_pile(self):
        src = Pile([self.ace, self.two])
        dst = Pile([])

        src.move_card_to_pile(self.ace, dst, face_up=False)
        self.assertEqual(src.cards, [self.two])
        self.assertEqual(dst.cards, [self.ace])
        self.assertFalse(self.ace.face_up)

        with self.assertRaises(ValueError):
            src.move_card_to_pile(self.three_down, dst)

    def test_move_top_card_to_pile(self):
        src = Pile([self.ace, self.three_down])
        dst = Pile([])

        src.move_top_card_to_pile(dst, face_up=True)
        self.assertEqual(src.cards, [self.ace])
        self.assertEqual(dst.cards, [self.three_down])
        self.assertTrue(self.three_down.face_up)

        Pile([]).move_top_card_to_pile(dst)
        self.assertEqual(len(dst), 1)

    def test_move_to_pile(self):
        src = Pile([self.ace, self.two])
        dst = Pile([self.three_down])

        src.move_to_pile(dst, face_up=False)
        self.assertTrue(src.is_empty())
        self.assertEqual(dst.cards, [self.three_down, self.two, self.ace])
        self.assertTrue(all(not c.face_up for c in dst.cards))

        src.move_to_pile(dst, face_up=True)
        self.assertEqual(len(dst), 3)

    def test_shuffle(self):
        cards = [Card(Rank(r), Suit.SPADE) for r in range(1, 14)]
        pile = Pile(list(cards))
        pile.shuffle()
        self.assertEqual(len(pile), 13)
        self.assertEqual(set(pile.cards), set(cards))

        empty = Pile([])
        empty.shuffle()
        self.assertEqual(len(empty), 0)

    def test_get_height(self):
        pile = Pile([self.ace, self.two])
        self.assertEqual(pile.get_height(), Pile.HEIGHT)
        self.assertEqual(pile.get_height(stretched=True), 7)

        stretched = Pile([self.ace, self.two], stretched=True)
        self.assertEqual(stretched.get_height(), 7)
        self.assertEqual(stretched.get_height(stretched=False), Pile.HEIGHT)

    def test_get_card_at_offset(self):
        pile = Pile([self.ace, self.two])
        self.assertEqual(pile.get_card_at_offset(0), 0)
        self.assertEqual(pile.get_card_at_offset(1), 0)
        self.assertEqual(pile.get_card_at_offset(2), 1)
        self.assertEqual(pile.get_card_at_offset(6), 1)
        self.assertIsNone(pile.get_card_at_offset(-1))
        self.assertIsNone(pile.get_card_at_offset(7))
        self.assertIsNone(Pile([]).get_card_at_offset(0))
