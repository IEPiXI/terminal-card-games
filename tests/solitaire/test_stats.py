import unittest

from core.card import Card, Rank, Suit
from solitaire.game import SolitaireGame
from tests.solitaire.test_pile import full_foundation


class TestSolitaireStats(unittest.TestCase):
    def setUp(self):
        self.game = SolitaireGame()
        self.board = self.game.board

    def test_initial_stats_and_restart(self):
        self.assertEqual(self.board.moves, 0)
        self.assertEqual(self.board.timer.formatted_time(), '00:00')

        rendered = self.game.render()
        self.assertIn('Time: 00:00', rendered)
        self.assertIn('Moves: 0', rendered)

        self.board.moves = 5
        self.game.restart()
        self.assertEqual(self.board.moves, 0)
        self.assertEqual(self.board.timer.formatted_time(), '00:00')

    def test_move_counting(self):
        # stock draw
        self.board.choose_pile()
        self.assertEqual(self.board.moves, 1)

        # recycle waste into stock
        self.board.stock_pile.cards.clear()
        self.board.choose_pile()
        self.assertEqual(self.board.moves, 2)

        # empty stock with empty waste is a no-op
        self.board.stock_pile.cards.clear()
        self.board.choose_pile()
        self.assertEqual(self.board.moves, 2)

        # flip face-down card
        col = self.board.tableau[0]
        col.cards = [Card(Rank.KING, Suit.HEART, face_up=False)]
        self.board.navigate_to_coordinate(1, 0)
        self.board.choose_pile()
        self.assertEqual(self.board.moves, 3)

        # invalid move
        self.board.choose_pile()
        self.board.navigate_to_coordinate(0, 0)
        self.board.choose_pile()
        self.assertEqual(self.board.moves, 3)

        # valid move
        col.cards = [Card(Rank.ACE, Suit.SPADE, face_up=True)]
        self.assertTrue(self.board.auto_move_to_foundation(col))
        self.assertEqual(self.board.moves, 4)

    def test_win_freezes_timer(self):
        for idx, suit in enumerate(Suit):
            self.board.foundations[idx].cards = full_foundation(suit)
        self.assertTrue(self.board.is_won())
        self.assertFalse(self.board.timer.is_running)
