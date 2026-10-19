import unittest

from core.card import Card, Rank, Suit
from scoundrel.pile import ScoundrelPile, card_value, is_monster, is_potion, is_weapon


class TestScoundrelPile(unittest.TestCase):
    def setUp(self):
        self.weapon_6 = Card(Rank.SIX, Suit.DIAMOND, face_up=True)
        self.monster_q = Card(Rank.QUEEN, Suit.SPADE, face_up=True)
        self.monster_7 = Card(Rank.SEVEN, Suit.CLUB, face_up=True)
        self.monster_ace = Card(Rank.ACE, Suit.SPADE, face_up=True)
        self.potion_5 = Card(Rank.FIVE, Suit.HEART, face_up=True)

    def test_card_helpers_and_values(self):
        self.assertEqual(card_value(self.weapon_6), 6)
        self.assertEqual(card_value(self.monster_q), 12)
        self.assertEqual(card_value(self.monster_ace), 14)

        self.assertTrue(is_monster(self.monster_q))
        self.assertFalse(is_monster(self.weapon_6))
        self.assertFalse(is_monster(None))

        self.assertTrue(is_weapon(self.weapon_6))
        self.assertFalse(is_weapon(self.potion_5))

        self.assertTrue(is_potion(self.potion_5))
        self.assertFalse(is_potion(self.monster_7))

    def test_selection_lifecycle(self):
        pile = ScoundrelPile([self.weapon_6])
        self.assertFalse(pile.is_selected)
        self.assertEqual(pile.selected_cards, [])

        pile.select()
        self.assertTrue(pile.is_selected)
        self.assertEqual(pile.selected_cards, [self.weapon_6])

        pile.deselect()
        self.assertFalse(pile.is_selected)
        self.assertEqual(pile.selected_cards, [])

        empty = ScoundrelPile([])
        empty.select()
        self.assertTrue(empty.is_selected)
        self.assertEqual(empty.selected_cards, [])

    def test_weapon_stack_inspection_and_limits(self):
        pile = ScoundrelPile([], stretched=True)
        self.assertIsNone(pile.get_weapon_card())
        self.assertEqual(pile.get_slain_monsters(), [])
        self.assertIsNone(pile.get_last_slain_monster())
        self.assertEqual(pile.get_weapon_value(), 0)
        self.assertIsNone(pile.get_max_monster_value())
        self.assertFalse(pile.can_slay_monster(self.monster_7))

        # fresh weapon can slay any monster up to Ace (14)
        pile.cards = [self.weapon_6]
        self.assertEqual(pile.get_weapon_card(), self.weapon_6)
        self.assertEqual(pile.get_weapon_value(), 6)
        self.assertEqual(pile.get_max_monster_value(), 14)
        self.assertTrue(pile.can_slay_monster(self.monster_ace))
        self.assertFalse(pile.can_slay_monster(self.potion_5))

        # after slaying Queen (12), can slay <= 12 (e.g. Q or 7), but not Ace (14)
        pile.cards.append(self.monster_q)
        self.assertEqual(pile.get_slain_monsters(), [self.monster_q])
        self.assertEqual(pile.get_last_slain_monster(), self.monster_q)
        self.assertEqual(pile.get_max_monster_value(), 12)
        self.assertTrue(pile.can_slay_monster(self.monster_q))
        self.assertTrue(pile.can_slay_monster(self.monster_7))
        self.assertFalse(pile.can_slay_monster(self.monster_ace))

    def test_move_top_card_to_bottom(self):
        c1 = Card(Rank.TWO, Suit.CLUB, face_up=True)
        c2 = Card(Rank.THREE, Suit.CLUB, face_up=True)
        src = ScoundrelPile([c1])
        dungeon = ScoundrelPile([c2])

        src.move_top_card_to_bottom(dungeon, face_up=False)
        self.assertTrue(src.is_empty())
        self.assertEqual(dungeon.cards, [c1, c2])
        self.assertFalse(c1.face_up)
