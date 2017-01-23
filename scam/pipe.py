import time

class Runner(object):
    """
    Runs the given pipes once using the first pipe as the starting point
    """
    def __init__(self, pipes, context):
       self.pipes = pipes
       self.context = context

    def error_pipe(self, index, exception):
        if index >= len(self.pipes):
            return lambda: None
        current_pipe = self.pipes[index]
        return lambda: current_pipe.error(self.context, exception, self.error_pipe(index + 1, exception))


    def run_pipe(self, index):
        if index >= len(self.pipes):
            return lambda: None
        current_pipe = self.pipes[index]

        def do_it():
            try:
                current_pipe.run(self.context, self.run_pipe(index + 1))
            except Exception as e:
                self.error_pipe(index, e)()
        return do_it

    def run(self):
        self.run_pipe(0)()

class LoopRunner(Runner):
    """
    Runs the pipeline constantly, sleeping for `sleep_seconds` between runs
    """
    def __init__(self, pipes, context, sleep_seconds=None):
        self.sleep_seconds = sleep_seconds
        self.running = True
        super().__init__(pipes, context)

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            super().run()
            if self.sleep_seconds is not None:
                time.sleep(self.sleep_seconds)
        


class Pipe(object):
    """
    Basic building block of a pipeline.
    """
    def run(self, context, next_run):
        """
        Runs the stage of the pipeline. The next callback should be called to continue control
        """
        return next_run()

    def error(self, context, exception, next_run):
        """
        Called if run fails, with the optional
        """
        return next_run()
