import unittest

from core.card import Card, Rank, Suit
from scoundrel.board import Board
from scoundrel.game import ScoundrelGame
from scoundrel.pile import is_monster, is_potion, is_weapon
from tests.core.test_engine_and_menu import trigger_key


class TestScoundrelBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

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

    def test_initial_deck_composition_and_deal(self):
        all_cards = [*self.board.dungeon_pile.cards, *(c for p in self.board.room for c in p.cards)]
        self.assertEqual(len(all_cards), 44)
        self.assertEqual(len(self.board.dungeon_pile), 40)
        self.assertEqual(self.board.room_card_count, 4)
        self.assertEqual(sum(1 for c in all_cards if is_monster(c)), 26)
        self.assertEqual(sum(1 for c in all_cards if is_weapon(c)), 9)
        self.assertEqual(sum(1 for c in all_cards if is_potion(c)), 9)
        self.assertTrue(all(p.get_top_card().face_up for p in self.board.room))
        self.assertEqual(self.board.health, 20)

    def test_avoid_room_and_consecutive_restriction(self):
        initial_room = [p.get_top_card() for p in self.board.room]
        self.assertTrue(self.board.can_avoid_room())
        self.assertTrue(self.board.avoid_room())

        # cannot avoid two rooms in a row
        self.assertTrue(self.board.avoided_last_turn)
        self.assertFalse(self.board.can_avoid_room())
        self.assertFalse(self.board.avoid_room())

        # the 4 avoided cards are face-down at the bottom of the dungeon
        self.assertEqual(self.board.dungeon_pile.cards[:4], initial_room[::-1])
        self.assertTrue(all(not c.face_up for c in self.board.dungeon_pile.cards[:4]))

    def test_cannot_avoid_after_taking_card(self):
        self._set_room(
            Card(Rank.FIVE, Suit.DIAMOND),
            Card(Rank.THREE, Suit.CLUB),
            Card(Rank.FOUR, Suit.CLUB),
            Card(Rank.SIX, Suit.CLUB),
        )
        self.board.equip_weapon(self.board.room[0])
        self.assertFalse(self.board.can_avoid_room())

    def test_weapon_equip_and_replacement_discards_previous_stack(self):
        w5 = Card(Rank.FIVE, Suit.DIAMOND)
        m8 = Card(Rank.EIGHT, Suit.SPADE)
        w7 = Card(Rank.SEVEN, Suit.DIAMOND)
        m2 = Card(Rank.TWO, Suit.CLUB)
        self._set_room(w5, m8, w7, m2)

        # equip 5♦ and slay 8♠ with it (taking 3 damage -> 17 HP)
        self.assertTrue(self.board.equip_weapon(self.board.room[0]))
        self.assertEqual(self.board.equipped_weapon, w5)
        self.assertTrue(self.board.fight_monster(self.board.room[1], use_weapon=True))
        self.assertEqual(self.board.health, 17)
        self.assertEqual(self.board.slain_monsters, [m8])

        # equipping 7♦ discards both 5♦ and 8♠ face-down
        self.assertTrue(self.board.equip_weapon(self.board.room[2]))
        self.assertEqual(self.board.equipped_weapon, w7)
        self.assertEqual(self.board.slain_monsters, [])
        self.assertIn(w5, self.board.discard_pile.cards)
        self.assertIn(m8, self.board.discard_pile.cards)
        self.assertTrue(all(not c.face_up for c in self.board.discard_pile.cards))

    def test_weapon_non_increasing_monster_limit_and_barehanded_fallback(self):
        w5 = Card(Rank.FIVE, Suit.DIAMOND)
        m6 = Card(Rank.SIX, Suit.CLUB)
        m_queen = Card(Rank.QUEEN, Suit.SPADE)
        m4 = Card(Rank.FOUR, Suit.SPADE)
        self.board.dungeon_pile.cards.clear()
        self._set_room(w5, m6, m_queen, m4)

        self.board.equip_weapon(self.board.room[0])
        # slay 6♣ with 5♦ (1 damage -> 19 HP, weapon cap is now <= 6)
        self.assertTrue(self.board.fight_monster(self.board.room[1], use_weapon=True))
        self.assertEqual(self.board.health, 19)

        # queen (12) > 6 -> cannot use weapon, must fight barehanded (12 damage -> 7 HP)
        self.assertFalse(self.board.can_fight_with_weapon(m_queen))
        self.assertFalse(self.board.fight_monster(self.board.room[2], use_weapon=True))
        self.assertTrue(self.board.fight_monster(self.board.room[2], use_weapon=False))
        self.assertEqual(self.board.health, 7)

        # weapon is still retained and can slay 4♠ (4 <= 6, 0 damage)
        self.assertTrue(self.board.can_fight_with_weapon(m4))
        self.assertTrue(self.board.fight_monster(self.board.room[3], use_weapon=True))
        self.assertEqual(self.board.health, 7)

    def test_health_potion_once_per_turn_and_max_cap(self):
        self.board.health = 14
        p5 = Card(Rank.FIVE, Suit.HEART)
        p4 = Card(Rank.FOUR, Suit.HEART)
        p9 = Card(Rank.NINE, Suit.HEART)
        m2 = Card(Rank.TWO, Suit.CLUB)
        self._set_room(p5, p4, p9, m2)

        # first potion heals +5 -> 19 HP
        self.assertTrue(self.board.use_potion(self.board.room[0]))
        self.assertEqual(self.board.health, 19)

        # second potion in same turn is discarded with no healing -> still 19 HP
        self.assertTrue(self.board.use_potion(self.board.room[1]))
        self.assertEqual(self.board.health, 19)

        # third card completes the 3-card turn and starts a new turn; next potion caps at 20
        self.assertTrue(self.board.fight_monster(self.board.room[3], use_weapon=False))
        self.assertEqual(self.board.health, 17)
        self.assertFalse(self.board.potion_used_this_turn)
        self.assertTrue(self.board.use_potion(self.board.room[2]))
        self.assertEqual(self.board.health, 20)

    def test_turn_completion_leaves_fourth_card_and_refills_room(self):
        c1 = Card(Rank.TWO, Suit.CLUB)
        c2 = Card(Rank.THREE, Suit.CLUB)
        c3 = Card(Rank.FOUR, Suit.CLUB)
        c4 = Card(Rank.FIVE, Suit.DIAMOND)
        self._set_room(c1, c2, c3, c4)

        self.board.auto_resolve_card(self.board.room[0])
        self.board.auto_resolve_card(self.board.room[1])
        self.assertEqual(self.board.room_card_count, 2)

        # resolving 3rd card triggers refill of the 3 empty slots while keeping c4
        self.board.auto_resolve_card(self.board.room[2])
        self.assertEqual(self.board.room_card_count, 4)
        self.assertEqual(self.board.room[3].get_top_card(), c4)
        self.assertEqual(self.board.cards_taken_this_turn, 0)

    def test_win_and_loss_scoring(self):
        # 1. loss score: negative sum of remaining monsters in dungeon + room
        self.board.health = 5
        self.board.dungeon_pile.cards = [
            Card(Rank.TEN, Suit.SPADE),
            Card(Rank.SEVEN, Suit.HEART),
        ]
        self._set_room(
            Card(Rank.ACE, Suit.CLUB),
            Card(Rank.FOUR, Suit.SPADE),
            Card(Rank.TWO, Suit.DIAMOND),
            Card(Rank.THREE, Suit.HEART),
        )
        # fighting Ace (14) barehanded drops health to 0; remaining monsters are 10♠ and 4♠ -> -14
        self.board.fight_monster(self.board.room[0], use_weapon=False)
        self.assertTrue(self.board.is_lost())
        self.assertFalse(self.board.is_won())
        self.assertEqual(self.board.get_score(), -14)

        # 2. win score with final health potion bonus at 20 HP
        self.board.reset()
        self.board.dungeon_pile.cards.clear()
        self.board.health = 18
        potion_6 = Card(Rank.SIX, Suit.HEART)
        self._set_room(potion_6)
        self.board.use_potion(self.board.room[0])
        self.assertTrue(self.board.is_won())
        self.assertEqual(self.board.health, 20)
        self.assertEqual(self.board.get_score(), 26)

    def test_choose_pile_and_navigation(self):
        w6 = Card(Rank.SIX, Suit.DIAMOND)
        m8 = Card(Rank.EIGHT, Suit.CLUB)
        p4 = Card(Rank.FOUR, Suit.HEART)
        m2 = Card(Rank.TWO, Suit.SPADE)
        self._set_room(w6, m8, p4, m2)

        # select w6 at (0, 2) and move down to weapon_pile at (1, 2)
        self.board.navigate_to_coordinate(0, 2)
        self.board.choose_pile()
        self.assertEqual(self.board.from_pile, self.board.room[0])
        self.board.navigate_board('down')
        self.assertEqual(self.board.current_selection, (1, 2))
        self.board.choose_pile()
        self.assertEqual(self.board.equipped_weapon, w6)

        # pressing up returns to the previous top-row column (0, 2)
        self.board.navigate_board('up')
        self.assertEqual(self.board.current_selection, (0, 2))


class TestScoundrelGame(unittest.TestCase):
    def test_keybindings_jump_and_actions(self):
        game = ScoundrelGame()
        trigger_key(game.kb, '1')
        self.assertEqual(game.board.current_selection, (0, 2))
        trigger_key(game.kb, '4')
        self.assertEqual(game.board.current_selection, (0, 5))
        trigger_key(game.kb, '5')
        self.assertEqual(game.board.current_selection, (1, 2))
        trigger_key(game.kb, '0')
        self.assertEqual(game.board.current_selection, (0, 0))
        trigger_key(game.kb, 'v')
        self.assertTrue(game.board.avoided_last_turn)

    def test_direct_play_via_space_and_enter(self):
        game = ScoundrelGame()
        board = game.board
        w5 = Card(Rank.FIVE, Suit.DIAMOND)
        p4 = Card(Rank.FOUR, Suit.HEART)
        m8 = Card(Rank.EIGHT, Suit.SPADE)
        m2 = Card(Rank.TWO, Suit.CLUB)
        for i, card in enumerate((w5, p4, m8, m2)):
            card.face_up = True
            board.room[i].cards = [card]
        board.health = 16
        board.cards_taken_this_turn = 0
        board.potion_used_this_turn = False

        # 1. On slot 1 (5♦ weapon): pressing Enter ('c-m') equips directly without manual pile hopping
        board.navigate_to_coordinate(0, 2)
        trigger_key(game.kb, 'c-m')
        self.assertEqual(board.equipped_weapon, w5)

        # 2. Cursor auto-advanced to slot 2 (4♥ potion): pressing 'p' drinks it
        self.assertEqual(board.current_selection, (0, 3))
        trigger_key(game.kb, 'p')
        self.assertEqual(board.health, 20)

        # 3. Cursor auto-advanced to slot 3 (8♠ monster): pressing Space (' ') fights with weapon
        self.assertEqual(board.current_selection, (0, 4))
        trigger_key(game.kb, ' ')
        self.assertEqual(board.health, 17)  # 20 - (8 - 5) = 17
        self.assertEqual(board.last_slain_monster, m8)

    def test_cursor_auto_advancement(self):
        board = Board()
        w6 = Card(Rank.SIX, Suit.DIAMOND)
        m4 = Card(Rank.FOUR, Suit.CLUB)
        p3 = Card(Rank.THREE, Suit.HEART)
        m9 = Card(Rank.NINE, Suit.SPADE)
        for i, card in enumerate((w6, m4, p3, m9)):
            card.face_up = True
            board.room[i].cards = [card]
        board.cards_taken_this_turn = 0

        # Start at room slot 1
        board.navigate_to_coordinate(0, 2)
        board.equip_weapon(board.room[0])
        # Cursor automatically advances to slot 2
        self.assertEqual(board.current_selection, (0, 3))

        board.fight_monster(board.room[1], use_weapon=True)
        # Cursor advances to slot 3
        self.assertEqual(board.current_selection, (0, 4))

    def test_hud_action_preview_and_victory(self):
        board = Board()
        w5 = Card(Rank.FIVE, Suit.DIAMOND)
        m8 = Card(Rank.EIGHT, Suit.SPADE)
        m10 = Card(Rank.TEN, Suit.CLUB)
        p4 = Card(Rank.FOUR, Suit.HEART)
        for i, card in enumerate((w5, m8, m10, p4)):
            card.face_up = True
            board.room[i].cards = [card]
        board.cards_taken_this_turn = 0
        board.health = 20

        # Preview on Weapon card
        board.navigate_to_coordinate(0, 2)
        hud = '\n'.join(''.join(row) for row in board._build_hud_rows())
        self.assertIn('Equip', hud)
        self.assertIn('Power 5', hud)

        # Equip weapon and preview monster combat
        board.equip_weapon(board.room[0])
        board.navigate_to_coordinate(0, 3)  # 8♠
        hud = '\n'.join(''.join(row) for row in board._build_hud_rows())
        self.assertIn('Weapon', hud)
        self.assertIn('Bare', hud)

        # Slay 8♠ -> weapon limit is now <= 8. Preview 10♣ (unusable with weapon)
        board.fight_monster(board.room[1], use_weapon=True)
        board.navigate_to_coordinate(0, 4)  # 10♣
        hud = '\n'.join(''.join(row) for row in board._build_hud_rows())
        self.assertIn('Unusable', hud)

        # Victory banner test
        board.health = 20
        board.dungeon_pile.cards.clear()
        for p in board.room:
            p.cards.clear()
        self.assertTrue(board.is_won())
        hud_win = '\n'.join(''.join(row) for row in board._build_hud_rows())
        self.assertIn('VICTORY', hud_win)

