import os
import unittest
import datetime
import time
from scam import detect, pipe

class ContourMatcherTestCase(unittest.TestCase):
    def load_snapshot(self, name, context):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'resources', name), 'rb') as fh:
            context['SOURCE_EXTENSION'] = '.jpeg'
            context['SOURCE_RAW_CONTENT'] = fh.read()

    def test_match_success(self):
        # Arrange
        context = {}
        self.load_snapshot('snapshot1.jpg', context)
        matcher = detect.ContourMatcher()
        matcher.run(context, lambda: None)
        self.load_snapshot('snapshot2.jpg', context)

        is_match = False
        def on_match():
            nonlocal is_match
            is_match = True

        # Act
        matcher.run(context, on_match)

        # Act
        self.assertTrue(is_match)

    def test_match_same_false(self):
        # Arrange
        context = {}
        self.load_snapshot('snapshot1.jpg', context)
        matcher = detect.ContourMatcher()
        matcher.run(context, lambda: None)
        self.load_snapshot('snapshot1.jpg', context)

        is_match = False
        def on_match():
            nonlocal is_match
            is_match = True

        # Act
        matcher.run(context, on_match)

        # Act
        self.assertFalse(is_match)


class IntervalMatcherTestCase(unittest.TestCase):
    def test_match_success(self):
        # Arrange
        context = {}
        matcher = detect.IntervalMatcher(time_delta=datetime.timedelta(seconds=1))

        is_match = False
        def on_match():
            nonlocal is_match
            is_match = True

        # Act
        matcher.run(context, on_match)
        self.assertFalse(is_match)

        time.sleep(1.1)
        matcher.run(context, on_match)

        # Act
        self.assertTrue(is_match)