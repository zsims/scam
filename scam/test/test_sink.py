import unittest
import tempfile
import shutil
import os
import datetime
from scam import sink


class ScopedTemporaryDirectory(object):
    def __init__(self):
        self.full_path = tempfile.mkdtemp()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.full_path, ignore_errors=True)


class FileSystemSinkTest(unittest.TestCase):
    def test_save_snapshot_success(self):
        # Arrange
        with ScopedTemporaryDirectory() as td:
            file_system_sink = sink.FileSystemSink(td.full_path)
            context = {
                'SOURCE_RAW_CONTENT': b'hi',
                'SOURCE_EXTENSION': '.jpeg',
                'SOURCE_NAME': 'Test',
                'SOURCE_DATE': datetime.datetime.now()
            }

            # Act
            file_system_sink.run(context, lambda: None)

            # Assert
            files = os.listdir(td.full_path)
            self.assertEqual(len(files), 1)
            first_file = files[0]
            self.assertTrue(first_file.endswith('.jpeg'))
            with open(os.path.join(td.full_path, first_file), 'rb') as fh:
                self.assertEqual(fh.read(), b'hi')


