
class Runner(object):
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

class Pipe(object):
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
