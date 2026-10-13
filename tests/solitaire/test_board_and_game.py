import unittest

from core.card import Card, Rank, Suit
from solitaire.board import Board
from solitaire.game import SolitaireGame
from tests.core.test_engine_and_menu import trigger_key
from tests.solitaire.test_pile import full_foundation


class TestSolitaireBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def _fill_foundations(self, count: int = 4):
        for idx, suit in enumerate(list(Suit)[:count]):
            self.board.foundations[idx].cards = full_foundation(suit)

    def _select_and_move(self, from_coord: tuple[int, int], to_coord: tuple[int, int], extra_cards: int = 0):
        self.board.navigate_to_coordinate(*from_coord)
        self.board.choose_pile()
        for _ in range(extra_cards):
            self.board.increase_select_count()
        self.board.navigate_to_coordinate(*to_coord)
        self.board.choose_pile()

    def test_initial_deal_layout(self):
        self.assertEqual(len(self.board.tableau), 7)
        for i, pile in enumerate(self.board.tableau):
            self.assertEqual(len(pile), i + 1)
            self.assertTrue(pile.get_top_card().face_up)
            self.assertTrue(all(not c.face_up for c in pile.cards[:-1]))

        self.assertEqual(sum(len(p) for p in self.board.tableau), 28)
        self.assertEqual(len(self.board.stock_pile), 24)
        self.assertTrue(self.board.waste_pile.is_empty())
        self.assertTrue(all(f.is_empty() for f in self.board.foundations))

    def test_stock_draw_and_waste_recycle(self):
        # selecting a tableau pile first is cancelled when clicking stock
        self.board.navigate_to_coordinate(1, 0)
        self.board.choose_pile()
        self.assertEqual(self.board.from_pile, self.board.tableau[0])

        self.board.navigate_to_coordinate(0, 6)
        top_stock_card = self.board.stock_pile.get_top_card()
        self.board.choose_pile()

        self.assertIsNone(self.board.from_pile)
        self.assertEqual(self.board.waste_pile.cards, [top_stock_card])
        self.assertTrue(top_stock_card.face_up)
        # selection updates to the new top card of stock
        self.assertEqual(self.board.stock_pile.selected_cards, [self.board.stock_pile.get_top_card()])

        while not self.board.stock_pile.is_empty():
            self.board.choose_pile()
            if not self.board.stock_pile.is_empty():
                self.assertEqual(self.board.stock_pile.selected_cards, [self.board.stock_pile.get_top_card()])

        # empty stock has no selected cards
        self.assertEqual(self.board.stock_pile.selected_cards, [])

        waste_order = list(self.board.waste_pile.cards)
        self.board.choose_pile()
        self.assertTrue(self.board.waste_pile.is_empty())
        self.assertEqual(self.board.stock_pile.cards, waste_order[::-1])
        self.assertTrue(all(not c.face_up for c in self.board.stock_pile.cards))
        # recycled stock updates selection to the new top card
        self.assertEqual(self.board.stock_pile.selected_cards, [self.board.stock_pile.get_top_card()])

    def test_reveal_face_down_and_deselection(self):
        # clicking face-down top card flips it without selecting as from_pile
        col = self.board.tableau[0]
        col.get_top_card().face_up = False
        self.board.navigate_to_coordinate(1, 0)
        self.board.choose_pile()
        self.assertTrue(col.get_top_card().face_up)
        self.assertIsNone(self.board.from_pile)

        # clicking empty pile is a no-op
        col.cards.clear()
        self.board.choose_pile()
        self.assertIsNone(self.board.from_pile)

        # clicking same pile twice deselects
        self.board.navigate_to_coordinate(1, 1)
        self.board.choose_pile()
        self.assertEqual(self.board.from_pile, self.board.tableau[1])
        self.board.choose_pile()
        self.assertIsNone(self.board.from_pile)

    def test_tableau_moves(self):
        hidden = Card(Rank.ACE, Suit.DIAMOND, face_up=False)
        c8_spade = Card(Rank.EIGHT, Suit.SPADE, face_up=True)
        c7_heart = Card(Rank.SEVEN, Suit.HEART, face_up=True)
        self.board.tableau[0].cards = [hidden, c8_spade, c7_heart]
        self.board.tableau[1].cards = [Card(Rank.NINE, Suit.DIAMOND, face_up=True)]

        # valid multi-card move transfers cards and flips exposed card
        self._select_and_move((1, 0), (1, 1), extra_cards=1)
        self.assertEqual(len(self.board.tableau[1]), 3)
        self.assertEqual(self.board.tableau[0].cards, [hidden])
        self.assertTrue(hidden.face_up)
        self.assertIsNone(self.board.from_pile)

        # invalid move (same color) is rejected and keeps from_pile selected
        self.board.tableau[0].cards = [Card(Rank.SEVEN, Suit.SPADE, face_up=True)]
        self.board.tableau[1].cards = [Card(Rank.EIGHT, Suit.CLUB, face_up=True)]
        self._select_and_move((1, 0), (1, 1))
        self.assertEqual(self.board.from_pile, self.board.tableau[0])

        # moving to waste pile is blocked
        self.board.navigate_to_coordinate(0, 5)
        self.board.choose_pile()
        self.assertTrue(self.board.waste_pile.is_empty())

    def test_empty_column_and_foundation_moves(self):
        king = Card(Rank.KING, Suit.SPADE, face_up=True)
        queen = Card(Rank.QUEEN, Suit.HEART, face_up=True)
        ace_spade = Card(Rank.ACE, Suit.SPADE, face_up=True)

        # non-King to empty column rejected; King accepted
        self.board.tableau[0].cards = [queen]
        self.board.tableau[1].cards = []
        self._select_and_move((1, 0), (1, 1))
        self.assertTrue(self.board.tableau[1].is_empty())
        self.board.deselect_from_pile()

        self.board.tableau[0].cards = [king]
        self._select_and_move((1, 0), (1, 1))
        self.assertEqual(self.board.tableau[1].cards, [king])

        # waste to foundation and waste to tableau
        self.board.waste_pile.cards = [ace_spade]
        self._select_and_move((0, 5), (0, 0))
        self.assertEqual(self.board.foundations[0].cards, [ace_spade])

        self.board.waste_pile.cards = [queen]
        self._select_and_move((0, 5), (1, 1))
        self.assertEqual(self.board.tableau[1].cards, [king, queen])

    def test_win_conditions(self):
        self.assertFalse(self.board.is_won())

        # 3 full + 1 partial (12 cards) -> not won
        self._fill_foundations(3)
        last_suit = list(Suit)[3]
        self.board.foundations[3].cards = full_foundation(last_suit)[:12]
        self.assertFalse(self.board.is_won())

        # moving 52nd card into foundation 3 triggers win
        self.board.tableau[0].cards = [Card(Rank.KING, last_suit, face_up=True)]
        self._select_and_move((1, 0), (0, 3))
        self.assertTrue(self.board.is_won())

        # mixed suit rejected
        self.board.foundations[0].cards[-1] = Card(Rank.KING, Suit.HEART, face_up=True)
        self.assertFalse(self.board.is_won())

        # out-of-order rejected
        self._fill_foundations()
        f0 = self.board.foundations[0].cards
        f0[0], f0[1] = f0[1], f0[0]
        self.assertFalse(self.board.is_won())

        # duplicate suits rejected
        for f in self.board.foundations:
            f.cards = full_foundation(Suit.SPADE)
        self.assertFalse(self.board.is_won())

        # reset clears win state
        self._fill_foundations()
        self.assertTrue(self.board.is_won())
        self.board.reset()
        self.assertFalse(self.board.is_won())


class TestSolitaireGame(unittest.TestCase):
    def test_keybindings_jump_and_select(self):
        game = SolitaireGame()

        # jump to foundation 0 with '!'
        trigger_key(game.kb, '!')
        self.assertEqual(game.board.current_selection, (0, 0))

        # jump to stock with '^'
        trigger_key(game.kb, '^')
        self.assertEqual(game.board.current_selection, (0, 6))

        # jump to tableau col 0 with '1'
        trigger_key(game.kb, '1')
        self.assertEqual(game.board.current_selection, (1, 0))
