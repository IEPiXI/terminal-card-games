import unittest

from core.card import Card, Rank, Suit
from solitaire.game import SolitaireGame
from tests.core.test_mouse import make_click


class TestSolitaireMouse(unittest.TestCase):
    def setUp(self):
        self.game = SolitaireGame()
        self.board = self.game.board

    def _click_cell(self, row: int, col: int, y_offset: int = 1) -> bool:
        x = col * 6 + 2
        y = (0 if row == 0 else 6) + y_offset
        return self.game.handle_mouse(make_click(x, y))

    def test_click_stock_draws_and_recycles(self):
        top_stock = self.board.stock_pile.get_top_card()
        self.assertTrue(self._click_cell(0, 6))
        self.assertEqual(self.board.waste_pile.get_top_card(), top_stock)
        self.assertTrue(top_stock.face_up)

        while not self.board.stock_pile.is_empty():
            self._click_cell(0, 6)

        self.assertTrue(self._click_cell(0, 6))
        self.assertFalse(self.board.stock_pile.is_empty())
        self.assertTrue(self.board.waste_pile.is_empty())

    def test_tableau_selection_depth_and_deselection(self):
        c1 = Card(Rank.NINE, Suit.SPADE, face_up=True)
        c2 = Card(Rank.EIGHT, Suit.HEART, face_up=True)
        c3 = Card(Rank.SEVEN, Suit.SPADE, face_up=True)
        col = self.board.tableau[0]
        col.cards = [c1, c2, c3]

        # click middle card (c2 at y_offset=3) -> selects 2-card run [c3, c2]
        self.assertTrue(self._click_cell(1, 0, y_offset=3))
        self.assertEqual(self.board.from_pile, col)
        self.assertEqual(col.selected_cards, [c3, c2])

        # click base card (c1 at y_offset=1) -> expands selection to 3 cards
        self.assertTrue(self._click_cell(1, 0, y_offset=1))
        self.assertEqual(col.select_count, 3)

        # clicking the same card depth again deselects the pile
        self.assertTrue(self._click_cell(1, 0, y_offset=1))
        self.assertIsNone(self.board.from_pile)

    def test_face_down_card_interactions(self):
        # buried face-down card in column 1 (y_offset=1) is ignored
        self.assertFalse(self._click_cell(1, 1, y_offset=1))
        self.assertIsNone(self.board.from_pile)

        # exposed face-down top card in column 0 flips face-up without selecting
        col0 = self.board.tableau[0]
        col0.cards[0].face_up = False
        self.assertTrue(self._click_cell(1, 0))
        self.assertTrue(col0.cards[0].face_up)
        self.assertIsNone(self.board.from_pile)

    def test_valid_moves_via_mouse(self):
        c_7s = Card(Rank.SEVEN, Suit.SPADE, face_up=True)
        c_8h = Card(Rank.EIGHT, Suit.HEART, face_up=True)
        king = Card(Rank.KING, Suit.CLUB, face_up=True)

        self.board.waste_pile.cards = [c_7s]
        self.board.tableau[0].cards = [c_8h]
        self.board.tableau[1].cards = [king]
        self.board.tableau[2].cards = []

        # 1. Waste (7♠) -> Tableau 0 (8♥)
        self.assertTrue(self._click_cell(0, 5))
        self.assertTrue(self._click_cell(1, 0))
        self.assertEqual(self.board.tableau[0].cards, [c_8h, c_7s])
        self.assertIsNone(self.board.from_pile)

        # 2. Tableau 1 (K♣) -> Empty Tableau 2
        self.assertTrue(self._click_cell(1, 1))
        self.assertTrue(self._click_cell(1, 2))
        self.assertEqual(self.board.tableau[2].cards, [king])
        self.assertTrue(self.board.tableau[1].is_empty())

    def test_invalid_move_switches_selection(self):
        self.board.tableau[0].cards = [Card(Rank.SEVEN, Suit.SPADE, face_up=True)]
        self.board.tableau[1].cards = [Card(Rank.SEVEN, Suit.HEART, face_up=True)]

        self._click_cell(1, 0)
        self.assertEqual(self.board.from_pile, self.board.tableau[0])

        self._click_cell(1, 1)
        self.assertEqual(self.board.from_pile, self.board.tableau[1])

    def test_double_click_foundation_moves(self):
        ace = Card(Rank.ACE, Suit.SPADE, face_up=True)
        five = Card(Rank.FIVE, Suit.SPADE, face_up=True)
        self.board.tableau[0].cards = [ace]
        self.board.tableau[1].cards = [Card(Rank.NINE, Suit.HEART, face_up=False), ace]
        self.board.tableau[2].cards = [five]

        # 1. Double-clicking buried card (col 1, y_offset=1) is ignored
        self.assertFalse(self._click_cell(1, 1, y_offset=1))
        self.assertFalse(self._click_cell(1, 1, y_offset=1))
        self.assertTrue(all(f.is_empty() for f in self.board.foundations))

        # 2. Double-clicking unmovable card (5♠ on col 2) leaves it in place
        self._click_cell(1, 2)
        self._click_cell(1, 2)
        self.assertEqual(self.board.tableau[2].cards, [five])

        # 3. Double-clicking eligible top card (A♠ on col 0) moves it to foundation
        self._click_cell(1, 0)
        self.assertTrue(self._click_cell(1, 0))
        self.assertEqual(self.board.foundations[0].cards, [ace])
        self.assertTrue(self.board.tableau[0].is_empty())

    def test_card_border_lines_ignored(self):
        # top border line (____) and bottom border line (¯¯¯¯) do not select cards
        self.assertFalse(self._click_cell(0, 6, y_offset=0))  # stock top border
        self.assertFalse(self._click_cell(0, 6, y_offset=4))  # stock bottom border
        self.assertFalse(self._click_cell(1, 0, y_offset=0))  # tableau 0 top border
        self.assertFalse(self._click_cell(1, 0, y_offset=4))  # tableau 0 bottom border

        # intermediate card border (|____|) in stretched pile does not select cards
        col = self.board.tableau[0]
        col.cards = [Card(Rank.KING, Suit.HEART, face_up=True), Card(Rank.QUEEN, Suit.SPADE, face_up=True)]
        self.assertFalse(self._click_cell(1, 0, y_offset=2))  # divider between king and queen
        self.assertIsNone(self.board.from_pile)
