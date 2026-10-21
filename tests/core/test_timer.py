import unittest

from core.timer import GameTimer


class TestGameTimer(unittest.TestCase):
    def test_lifecycle(self):
        timer = GameTimer(start_now=False)
        self.assertFalse(timer.is_running)

        timer.start()
        self.assertTrue(timer.is_running)

        timer.stop()
        self.assertFalse(timer.is_running)

        timer.reset(start_now=False)
        self.assertFalse(timer.is_running)
        self.assertEqual(timer.elapsed_seconds, 0)

    def test_formatted_time(self):
        timer = GameTimer(start_now=False)
        self.assertEqual(timer.formatted_time(), '00:00')

        timer.start_time, timer.end_time = 0.0, 65.0
        self.assertEqual(timer.formatted_time(), '01:05')

        timer.end_time = 3665.0
        self.assertEqual(timer.formatted_time(), '01:01:05')
