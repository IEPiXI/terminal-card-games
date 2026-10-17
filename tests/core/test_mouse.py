import unittest
from unittest.mock import MagicMock

from prompt_toolkit.data_structures import Point
from prompt_toolkit.mouse_events import MouseButton, MouseEvent, MouseEventType

from core.board import Board
from core.card import Card, Rank, Suit
from core.engine import GameEngine, GameSpec
from core.game import Game
from core.mouse import BoardMouseController, GridHit, MouseTextControl
from core.pile import Pile
from menu import ScreenItem, SelectableScreen, TCGMenu


def make_click(x: int, y: int, button=MouseButton.LEFT, event_type=MouseEventType.MOUSE_UP) -> MouseEvent:
    return MouseEvent(Point(x, y), event_type, button, frozenset())


class MultiRowBoard(Board):
    """Board with 3 rows: row 0 unstretched, row 1 stretched (3 cards + spacer), row 2 unstretched."""

    def reset(self):
        cards = [Card(r, Suit.SPADE, face_up=True) for r in (Rank.ACE, Rank.TWO, Rank.THREE)]
        self.board = [
            [Pile([]), Pile([])],
            [Pile(cards, stretched=True), Pile(None)],
            [Pile([])],
        ]
        self.current_selection = (0, 0)


class TestBoardMouseController(unittest.TestCase):
    def setUp(self):
        self.board = MultiRowBoard()
        self.controller = BoardMouseController(self.board)

    def test_hit_test_invalid_coordinates(self):
        # out-of-bounds coordinates
        for x, y in ((-1, 0), (0, -1), (100, 0), (0, 100)):
            self.assertIsNone(self.controller.hit_test(x, y))

        # non-navigable spacer pile (row 1, col 1)
        self.assertIsNone(self.controller.hit_test(7, 7))

        # pile borders and indicator lines across rows 0-2 (col 0)
        # row 0: (0, 4, 5), row 1: (6, 14, 15), row 2: (16, 20, 21)
        for y in (0, 4, 5, 6, 14, 15, 16, 20, 21):
            self.assertIsNone(self.controller.hit_test(2, y))

    def test_hit_test_unstretched_rows(self):
        self.assertEqual(self.controller.hit_test(2, 2), GridHit(0, 0, None))
        self.assertEqual(self.controller.hit_test(8, 2), GridHit(0, 1, None))
        # row 2 starts at y=16 (borders at y=16 and y=20 are excluded; face rows at 17, 18, 19)
        self.assertEqual(self.controller.hit_test(2, 17), GridHit(2, 0, None))
        self.assertEqual(self.controller.hit_test(2, 19), GridHit(2, 0, None))

    def test_hit_test_stretched_row_card_indices(self):
        # row 1 cards: y=7, 8 card 0 (including divider |____|); y=9, 10 card 1; y=11..13 card 2
        for y in (7, 8):
            self.assertEqual(self.controller.hit_test(2, y), GridHit(1, 0, 0))
        for y in (9, 10):
            self.assertEqual(self.controller.hit_test(2, y), GridHit(1, 0, 1))
        for y in (11, 12, 13):
            self.assertEqual(self.controller.hit_test(2, y), GridHit(1, 0, 2))
        for y in (6, 14):
            self.assertIsNone(self.controller.hit_test(2, y))

    def test_click_navigation_and_ignored_events(self):
        self.assertFalse(self.controller.handle_mouse(make_click(2, 2, button=MouseButton.RIGHT)))
        self.assertFalse(self.controller.handle_mouse(make_click(2, 2, event_type=MouseEventType.MOUSE_DOWN)))

        self.assertTrue(self.controller.handle_mouse(make_click(2, 17)))
        self.assertEqual(self.board.current_selection, (2, 0))

    def test_double_click_lifecycle(self):
        double_clicked = []
        self.controller.on_double_click = lambda hit: double_clicked.append(hit) or True

        # clicking two different cards in the same column does not trigger double-click
        self.controller.handle_mouse(make_click(2, 7))
        self.controller.handle_mouse(make_click(2, 9))
        self.assertEqual(double_clicked, [])

        # two consecutive clicks on the same target trigger double-click once, then reset
        ev = make_click(2, 2)
        self.controller.handle_mouse(ev)
        self.controller.handle_mouse(ev)
        self.controller.handle_mouse(ev)
        self.assertEqual(double_clicked, [GridHit(0, 0, None)])

    def test_unhandled_double_click_resets_timer(self):
        self.controller.on_double_click = lambda hit: False
        ev = make_click(2, 2)
        self.controller.handle_mouse(ev)
        self.controller.handle_mouse(ev)
        self.assertIsNone(self.controller._last_click)


class TestMenuMouse(unittest.TestCase):
    @staticmethod
    def _click_text(screen: SelectableScreen, target: str, x_offset: int = 0) -> bool:
        lines = screen.render(color=False).split('\n')
        y = next(i for i, line in enumerate(lines) if target in line)
        x = lines[y].find(target) + x_offset
        return screen.handle_mouse(make_click(x, y))

    def test_click_menu_item_and_marker(self):
        selected = []
        screen = SelectableScreen(
            [ScreenItem('1', 'Game One', 'g1'), ScreenItem('2', 'Game Two', 'g2')],
            on_select=selected.append,
        )
        self.assertTrue(self._click_text(screen, '[2] Game Two'))
        self.assertEqual(screen.selected_idx, 1)
        self.assertEqual(selected[-1].value, 'g2')

        # clicking the '>' cursor marker (2 chars before item) also selects it
        self.assertTrue(self._click_text(screen, '[2]', x_offset=-2))
        self.assertEqual(len(selected), 2)

    def test_click_custom_formatted_item(self):
        class CustomScreen(SelectableScreen):
            def format_item(self, item: ScreenItem) -> str:
                return f'Option {item.key}: {item.label}'

        selected = []
        screen = CustomScreen([ScreenItem('A', 'Alpha', 'val_a')], on_select=selected.append)
        self.assertTrue(self._click_text(screen, 'Option A', x_offset=2))
        self.assertEqual(selected[0].value, 'val_a')

    def test_click_footer_hints(self):
        selected, quit_called = [], []
        menu = TCGMenu(
            [ScreenItem('1', 'Game', 'g1')],
            on_select=selected.append,
            on_quit=lambda: quit_called.append(True),
        )
        self.assertTrue(self._click_text(menu, '[Enter] Play', x_offset=1))
        self.assertEqual(len(selected), 1)

        self.assertTrue(self._click_text(menu, '[q] Quit', x_offset=1))
        self.assertEqual(len(quit_called), 1)


class TestEngineMouseIntegration(unittest.TestCase):
    def test_engine_routes_mouse_to_active_view(self):
        engine = GameEngine([GameSpec('dummy', 'Dummy', lambda: Game(MultiRowBoard()), '1')])
        engine.menu.handle_mouse = MagicMock(return_value=True)

        ev = make_click(5, 5)
        self.assertTrue(engine.handle_mouse_event(ev))
        engine.menu.handle_mouse.assert_called_once_with(ev)

    def test_mouse_text_control_handler_and_sentinel(self):
        control = MouseTextControl(on_mouse_event=lambda ev: ev.position.x == 10, text='Line 1\nLine 2')
        self.assertIsNone(control.mouse_handler(make_click(10, 0)))
        self.assertIs(control.mouse_handler(make_click(5, 0)), NotImplemented)

        ui_content = control.create_content(width=40, height=20)
        self.assertEqual(ui_content.line_count, 3)
        self.assertEqual(ui_content.get_line(0)[-1], ('', ' '))
        self.assertEqual(ui_content.get_line(2), [('', ' ')])

    def test_game_restart_resets_mouse(self):
        game = Game(MultiRowBoard())
        game.mouse.handle_mouse(make_click(2, 2))
        self.assertIsNotNone(game.mouse._last_click)

        game.restart()
        self.assertIsNone(game.mouse._last_click)
