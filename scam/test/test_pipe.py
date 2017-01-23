import unittest
from scam import pipe
import os
import threading

class PipeStub(pipe.Pipe):
    def __init__(self):
        self.run_called = False
        self.error_called = False

    def run(self, context, next_run):
        self.run_called = True
        return next_run()

    def error(self, context, exception, next_run):
        self.error_called = True
        return next_run()

class ErrorPipeStub(pipe.Pipe):
    def __init__(self):
        self.error_called = False

    def run(self, context, next_run):
        raise Exception('BOOM')

    def error(self, context, exception, next_run):
        self.error_called = True
        return next_run()

class PipeTestCase(unittest.TestCase):
    def load_snapshot(self, name, context):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'resources', name), 'rb') as fh:
            context['SOURCE_EXTENSION'] = '.jpeg'
            context['SOURCE_RAW_CONTENT'] = fh.read()

    def test_run_calls_next(self):
        # Arrange
        first = PipeStub()
        second = PipeStub()

        runner = pipe.Runner([first, second], {})

        # Act
        runner.run()

        # Assert
        self.assertTrue(second.run_called)

    def test_run_calls_next_error_on_exception(self):
        # Arrange
        first = PipeStub()
        second = ErrorPipeStub()
        third = PipeStub()

        runner = pipe.Runner([first, second, third], {})

        # Act
        runner.run()

        # Assert
        self.assertTrue(first.run_called)
        self.assertFalse(first.error_called)
        self.assertTrue(second.error_called)
        self.assertFalse(third.run_called)
        self.assertTrue(third.error_called)

class AnyTestCase(unittest.TestCase):
    def test_run_calls_next_lazy(self):
        # Arrange
        first = PipeStub()
        second = pipe.Any([
            PipeStub(),
            PipeStub()
        ])
        third = PipeStub()

        runner = pipe.Runner([first, second, third], {})

        # Act
        runner.run()

        # Assert
        self.assertTrue(second.pipes[0].run_called)
        self.assertFalse(second.pipes[1].run_called)
        self.assertTrue(third.run_called)

    def test_run_calls_next_if_first_fails(self):
        # Arrange
        first = PipeStub()
        second = pipe.Any([
            pipe.CallbackPipe(lambda context, run_next: None),
            PipeStub(),
            PipeStub()
        ])
        third = PipeStub()

        runner = pipe.Runner([first, second, third], {})

        # Act
        runner.run()

        # Assert
        self.assertTrue(second.pipes[1].run_called)
        self.assertFalse(second.pipes[2].run_called)
        self.assertTrue(third.run_called)

class LoopRunnerTestCase(unittest.TestCase):
    def test_run_calls_next(self):
        # Arrange
        first = PipeStub()
        second = PipeStub()

        finish_event = threading.Event()
        call_count = 0
        def do_it(context, run_next):
            nonlocal call_count
            if call_count > 0:
                finish_event.set()
            call_count = call_count + 1

        third = pipe.CallbackPipe(do_it)
        runner = pipe.LoopRunner([first, second, third], {})

        # Act
        threading.Thread(target=runner.run).start()

        # Assert
        finish_event.wait(timeout=2)
        runner.stop()
        self.assertTrue(finish_event.is_set())
