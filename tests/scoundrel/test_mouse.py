import unittest

from core.card import Card, Rank, Suit
from scoundrel.game import ScoundrelGame
from tests.core.test_mouse import make_click


class TestScoundrelMouse(unittest.TestCase):
    def setUp(self):
        self.game = ScoundrelGame()
        self.board = self.game.board

    def _click_cell(self, row: int, col: int, y_offset: int = 1) -> bool:
        x = col * 6 + 2
        y = (0 if row == 0 else 6) + y_offset
        return self.game.handle_mouse(make_click(x, y))

    def _set_room(self, *cards: Card):
        for i, pile in enumerate(self.board.room):
            if i < len(cards) and cards[i] is not None:
                cards[i].face_up = True
                pile.cards = [cards[i]]
            else:
                pile.cards = []
            pile.reset_selection()
        self.board.cards_taken_this_turn = 0
        self.board.potion_used_this_turn = False

    def test_click_dungeon_avoids_room_once(self):
        self.assertTrue(self._click_cell(0, 0))
        self.assertTrue(self.board.avoided_last_turn)
        # second consecutive click on dungeon is rejected
        self.assertFalse(self._click_cell(0, 0))

    def test_select_and_move_via_mouse(self):
        w5 = Card(Rank.FIVE, Suit.DIAMOND)
        m8 = Card(Rank.EIGHT, Suit.SPADE)
        p4 = Card(Rank.FOUR, Suit.HEART)
        m2 = Card(Rank.TWO, Suit.CLUB)
        self._set_room(w5, m8, p4, m2)

        # 1. click room[0] (5♦) then click weapon pile (1, 2) to equip
        self.assertTrue(self._click_cell(0, 2))
        self.assertEqual(self.board.from_pile, self.board.room[0])
        self.assertTrue(self._click_cell(1, 2))
        self.assertEqual(self.board.equipped_weapon, w5)
        self.assertIsNone(self.board.from_pile)

        # 2. click room[1] (8♠) then click discard pile (0, 7) to fight barehanded
        self.assertTrue(self._click_cell(0, 3))
        self.assertTrue(self._click_cell(0, 7))
        self.assertEqual(self.board.health, 12)
        self.assertEqual(self.board.slain_monsters, [])

        # 3. click room[2] (4♥) then click discard pile (0, 7) to drink potion
        self.assertTrue(self._click_cell(0, 4))
        self.assertTrue(self._click_cell(0, 7))
        self.assertEqual(self.board.health, 16)

    def test_double_click_auto_resolves_room_card(self):
        w6 = Card(Rank.SIX, Suit.DIAMOND)
        m9 = Card(Rank.NINE, Suit.CLUB)
        p3 = Card(Rank.THREE, Suit.HEART)
        m2 = Card(Rank.TWO, Suit.SPADE)
        self._set_room(w6, m9, p3, m2)

        # double-click 6♦ equips weapon
        self.assertTrue(self._click_cell(0, 2))
        self.assertTrue(self._click_cell(0, 2))
        self.assertEqual(self.board.equipped_weapon, w6)

        # double-click 9♣ fights with equipped weapon (9 - 6 = 3 damage -> 17 HP)
        self.assertTrue(self._click_cell(0, 3))
        self.assertTrue(self._click_cell(0, 3))
        self.assertEqual(self.board.health, 17)
        self.assertEqual(self.board.slain_monsters, [m9])
