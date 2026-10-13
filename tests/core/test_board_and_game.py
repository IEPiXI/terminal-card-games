import unittest

from core.board import Board
from core.game import Game
from core.pile import Pile


class DummyBoard(Board):
    """Simple 2x2 grid with a spacer at (0, 1) for testing base navigation."""

    def reset(self):
        self.board = [
            [Pile([]), Pile(None)],
            [Pile([]), Pile([])],
        ]
        self.current_selection = (0, 0)
        self.entered = []
        self.left = []

    def _on_leave(self, row: int, col: int):
        self.left.append((row, col))

    def _on_enter(self, row: int, col: int):
        self.entered.append((row, col))


class TestBaseBoardAndGame(unittest.TestCase):
    def test_board_defaults_and_lifecycle(self):
        board = Board()
        self.assertFalse(board.is_won())
        self.assertEqual(board.board, [])
        self.assertEqual(board.current_selection, (0, 0))

    def test_navigation_skips_spacers_and_fires_hooks(self):
        board = DummyBoard()

        # moving right from (0, 0) skips spacer at (0, 1) and wraps to (0, 0) -> no-op
        board.navigate_board('right')
        self.assertEqual(board.current_selection, (0, 0))
        self.assertEqual(board.entered, [])

        # moving down goes to (1, 0) and fires hooks
        board.navigate_board('down')
        self.assertEqual(board.current_selection, (1, 0))
        self.assertEqual(board.left, [(0, 0)])
        self.assertEqual(board.entered, [(1, 0)])

        # jumping to current coordinate is a no-op
        board.navigate_to_coordinate(1, 0)
        self.assertEqual(len(board.entered), 1)

        # jumping to spacer at (0, 1) is ignored
        board.navigate_to_coordinate(0, 1)
        self.assertEqual(board.current_selection, (1, 0))

    def test_base_game_delegation(self):
        board = DummyBoard()
        game = Game(board)

        self.assertFalse(game.is_won())
        board.navigate_to_coordinate(1, 1)
        game.restart()
        self.assertEqual(board.current_selection, (0, 0))
        self.assertTrue(isinstance(game.render(), str))
