import unittest
from unittest.mock import MagicMock

from core.board import Board
from core.engine import GameEngine, GameSpec, State
from core.game import Game
from core.pile import Pile
from menu import (
    ConfirmScreen,
    ScreenItem,
    SelectableScreen,
    TCGMenu,
    WinScreen,
    center_block,
    center_line,
    colorize_suits,
    render_hints,
    strip_ansi,
)


def trigger_key(kb, key: str, event=None):
    """Helper to invoke a prompt_toolkit keybinding by key name."""
    event = event or MagicMock()
    binding = next(b for b in kb.bindings if key in b.keys or any(getattr(k, 'value', k) == key for k in b.keys))
    binding.call(event)
    return event


class DummyPlayableBoard(Board):
    def reset(self):
        self.board = [[Pile([])]]
        self.current_selection = (0, 0)
        self.won = False

    def is_won(self) -> bool:
        return self.won


class DummyGame(Game):
    def __init__(self):
        super().__init__(DummyPlayableBoard())


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine([GameSpec('dummy', 'Dummy Game', DummyGame, '1')])

    def test_quit_prompts_confirmation_and_exits(self):
        event = trigger_key(self.engine.kb, 'q')
        self.assertTrue(self.engine.is_confirm)
        self.assertIn('Do you really want to quit?', self.engine.render())

        trigger_key(self.engine.confirm_screen.kb, 'y')
        self.assertFalse(self.engine.is_confirm)
        event.app.exit.assert_called_once()

    def test_menu_navigation_and_launch(self):
        trigger_key(self.engine.menu.kb, 'up')
        trigger_key(self.engine.menu.kb, 'c-m')
        self.assertEqual(self.engine.state, State.GAME)
        self.assertIsInstance(self.engine.game, DummyGame)
        self.assertIn('____', self.engine.render())

    def test_menu_shortcut_launches_game(self):
        trigger_key(self.engine.menu.kb, '1')
        self.assertEqual(self.engine.state, State.GAME)
        self.assertIsInstance(self.engine.game, DummyGame)

    def test_return_to_menu_prompts_confirmation(self):
        self.engine.start_game('dummy')
        trigger_key(self.engine.kb, 'm')
        self.assertTrue(self.engine.is_confirm)
        self.assertIn('Return to the main menu?', self.engine.render())

        trigger_key(self.engine.confirm_screen.kb, 'y')
        self.assertEqual(self.engine.state, State.MENU)
        self.assertIn('TERMINAL CARD GAMES', self.engine.render())

    def test_win_state_switches_active_view_and_allows_restart(self):
        self.engine.start_game('dummy')
        game = self.engine.game

        self.assertEqual(self.engine.active_view, game)
        self.assertNotIn('Congratulations!', self.engine.render())

        # win the game
        game.board.won = True
        self.assertTrue(self.engine.is_won)
        self.assertEqual(self.engine.active_view, self.engine.win_screen)
        self.assertIn('Congratulations!', self.engine.render())

        # 'r' restarts the game via win_screen
        trigger_key(self.engine.win_screen.kb, 'r')
        self.assertFalse(self.engine.is_won)
        self.assertEqual(self.engine.active_view, game)

    def test_confirm_cancel_restores_view_without_action(self):
        self.engine.start_game('dummy')

        # trigger restart confirmation and cancel with 'n'
        trigger_key(self.engine.kb, 'r')
        self.assertTrue(self.engine.is_confirm)
        trigger_key(self.engine.confirm_screen.kb, 'n')
        self.assertFalse(self.engine.is_confirm)
        self.assertEqual(self.engine.state, State.GAME)

        # trigger menu confirmation and cancel with 'escape'
        trigger_key(self.engine.kb, 'm')
        self.assertTrue(self.engine.is_confirm)
        trigger_key(self.engine.confirm_screen.kb, 'escape')
        self.assertFalse(self.engine.is_confirm)
        self.assertEqual(self.engine.state, State.GAME)


class TestScreens(unittest.TestCase):
    def test_tcg_menu(self):
        menu = TCGMenu(
            [
                ScreenItem('1', 'Game 1', 'g1'),
                ScreenItem('2', 'Game 2', 'g2'),
            ]
        )
        output = menu.render(color=False)
        self.assertIn('TERMINAL CARD GAMES', output)
        self.assertIn('Game 1', output)
        self.assertIn('[Enter] Play', output)
        self.assertIn('[q] Quit', output)

        self.assertEqual(menu.get_selected_game(), 'g1')
        menu.select_next()
        self.assertEqual(menu.get_selected_game(), 'g2')
        menu.select_prev()
        self.assertEqual(menu.get_selected_game(), 'g1')

    def test_win_screen_render(self):
        screen = WinScreen().render(color=False)
        self.assertIn('Congratulations!', screen)
        self.assertIn('You completed the game!', screen)
        self.assertIn('[r] Play Again', screen)
        self.assertIn('[m] Main Menu', screen)
        self.assertIn('[q] Quit', screen)

    def test_confirm_screen_confirm_and_cancel(self):
        result = None

        def on_close(confirmed: bool):
            nonlocal result
            result = confirmed

        screen = ConfirmScreen('Save progress?', on_close=on_close)

        # confirm via 'y' and 'Y'
        trigger_key(screen.kb, 'y')
        self.assertTrue(result)
        result = None
        trigger_key(screen.kb, 'Y')
        self.assertTrue(result)

        # cancel via 'n', 'N', and 'escape'
        trigger_key(screen.kb, 'n')
        self.assertFalse(result)
        result = None
        trigger_key(screen.kb, 'N')
        self.assertFalse(result)
        result = None
        trigger_key(screen.kb, 'escape')
        self.assertFalse(result)

    def test_selectable_screen_navigation_and_hotkeys(self):
        item_a = ScreenItem('A', 'Choice A', 'a')
        item_b = ScreenItem('B', 'Choice B', 'b')

        screen = SelectableScreen(
            [item_a, item_b],
            on_select=lambda it: setattr(screen, '_last', it),
        )
        rendered = screen.render(color=False)
        self.assertIn('> [A] Choice A <', rendered)
        self.assertIn('[B] Choice B', rendered)

        # enter triggers selection on current item
        trigger_key(screen.kb, 'c-m')
        self.assertEqual(getattr(screen, '_last'), item_a)

        # hotkey 'b' selects item_b
        trigger_key(screen.kb, 'b')
        self.assertEqual(getattr(screen, '_last'), item_b)

    def test_selectable_screen_empty_raises(self):
        with self.assertRaises(ValueError):
            SelectableScreen([])


class TestFormattingAndHelpers(unittest.TestCase):
    def test_screen_item_fields_and_defaults(self):
        item = ScreenItem('q', 'Quit')
        self.assertEqual(item.key, 'q')
        self.assertEqual(item.label, 'Quit')
        self.assertEqual(item.value, 'q')

        custom = ScreenItem('1', 'Solitaire', value='solitaire')
        self.assertEqual(custom.value, 'solitaire')

    def test_colorize_suits(self):
        self.assertEqual(colorize_suits('♠ ♥ ♦ ♣', color=False), '♠ ♥ ♦ ♣')

    def test_strip_ansi(self):
        self.assertEqual(strip_ansi('\x1b[31m♥\x1b[0m'), '♥')

    def test_alignment_helpers(self):
        self.assertEqual(center_line('TEST', width=10), '   TEST')
        self.assertEqual(center_block('A\nB', width=6), '  A\n  B')
        self.assertEqual(render_hints(ScreenItem('q', 'Quit'), width=14), '   [q] Quit')

    def test_screen_str_conversion(self):
        win_screen = WinScreen()
        self.assertEqual(str(win_screen), win_screen.render(color=False))
