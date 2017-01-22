import os
import abc
from scam import pipe
import dropbox
import sys


def _get_filename(context):
    """
    Calculates a suitable filename based on the source information in the given context
    """
    when = context['SOURCE_DATE'].strftime('%Y-%m-%dT%H %M %S')
    return '{} {}{}'.format(when, context['SOURCE_NAME'], context['SOURCE_EXTENSION'])

class FileSystemSink(pipe.Pipe):
    """
    Writes the source raw content to a file on disk
    """
    def __init__(self, full_path):
        self.full_path = full_path
        if not os.path.isdir(self.full_path):
            os.makedirs(self.full_path)

    def run(self, context, next_run):
        destination_path = os.path.join(self.full_path, _get_filename(context))
        with open(destination_path, 'wb') as fh:
            fh.write(context['SOURCE_RAW_CONTENT'])

        return next_run()


class LoggerSink(pipe.Pipe):
    """
    Logs all piped messages and errors, including printable parts of the context
    """
    def run(self, context, next_run):
        for key in context.keys():
            value = context[key]
            if isinstance(value, (str, int, float, complex)):
                print('{} = {}'.format(key, value))
        print('')
        return next_run()

    def error(self, context, exception, next_run):
        print(exception, file=sys.stderr)
        return next_run()


class DropboxSink(pipe.Pipe):
    """
    Uploads the source raw content to a path with-in Dropbox
    """
    def __init__(self, path_prefix, access_token):
        self.path_prefix = path_prefix
        self.client = dropbox.Dropbox(access_token)

    def run(self, context, next_run):
        destination_path = '{}{}'.format(self.path_prefix, _get_filename(context))
        self.client.files_upload(
            context['SOURCE_RAW_CONTENT'],
            destination_path,
            mode=dropbox.files.WriteMode('overwrite'))
        return next_run()
