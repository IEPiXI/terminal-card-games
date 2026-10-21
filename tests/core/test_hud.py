import unittest

from core.board import Board
from core.hud import HUDItem, format_stat_row, render_hud
from core.mouse import BoardMouseController
from core.pile import Pile
from core.utils import strip_ansi


class TestHUDAndCoreBoard(unittest.TestCase):
    def test_hud_item_rendering(self):
        self.assertEqual(HUDItem('Moves', 12).render(), 'Moves: 12')
        self.assertEqual(HUDItem('Moves', lambda: 15).render(), 'Moves: 15')
        self.assertEqual(HUDItem('', 'PAUSED').render(), 'PAUSED')

        colored_item = HUDItem('HP', 20, color='green')
        self.assertEqual(colored_item.render(color=False), 'HP: 20')
        self.assertIn('\x1b[', colored_item.render(color=True))

    def test_format_stat_row(self):
        self.assertEqual(format_stat_row([], width=20), '')
        self.assertEqual(format_stat_row([HUDItem('Moves', 5)], width=20), 'Moves: 5')

        row = format_stat_row([HUDItem('Time', '00:10'), HUDItem('Moves', 5)], width=30)
        self.assertTrue(row.startswith('Time: 00:10') and row.endswith('Moves: 5'))
        self.assertEqual(len(strip_ansi(row)), 30)

    def test_render_hud(self):
        self.assertEqual(render_hud([], width=20), [])

        lines = render_hud([HUDItem('Score', 100)], width=20)
        self.assertEqual(len(lines), 4)
        self.assertIn('Score: 100', lines[1])

    def test_board_hud_and_mouse_offset(self):
        board = Board()
        board.board = [[Pile([])]]
        self.assertEqual(board.get_header_height(), 0)

        board.get_hud_items = lambda: [HUDItem('Score', 10)]
        self.assertEqual(board.get_header_height(), 4)
        self.assertIn('Score: 10', board.get_print_string()[1][0])

        controller = BoardMouseController(board)
        self.assertIsNone(controller.hit_test(2, 0))
        self.assertEqual(controller.hit_test(2, 5).row, 0)
