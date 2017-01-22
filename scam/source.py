import datetime
import os
import requests
from requests.auth import HTTPBasicAuth
from scam import pipe


class SnapshotError(Exception):
    """
    Failed to get a snapshot from a camera
    """
    pass


class IpCamera(pipe.Pipe):
    """
    IP camera source with basic authentication
    """
    def __init__(self, name, authority, basic_username='admin', basic_password=''):
        self.name = name
        self.authority = authority
        self.auth = HTTPBasicAuth(basic_username, basic_password)
        self.snapshot_url = 'http://{}/snapshot.cgi'.format(authority)

    def _snapshot(self):
        """
        Requests a snapshot from the camera.
        :return: A Snapshot object from the camera
        """
        response = requests.get(self.snapshot_url, auth=self.auth)
        if response.status_code == 200:
            content_type = response.headers['content-type'] if 'content-type' in response.headers else 'application/octet-stream'
            return (response.content, content_type)
        raise SnapshotError('Failed to get snapshot from {}, error {}'.format(self.snapshot_url, response.status_code))

    def get_extension(self, mime):
        return '.jpeg'

    def run(self, context, next_run):
        (content, mime) = self._snapshot()
        context['SOURCE_NAME'] = self.name
        context['SOURCE_RAW_CONTENT'] = content
        context['SOURCE_EXTENSION'] = self.get_extension(mime)
        context['SOURCE_DATE'] = datetime.datetime.utcnow()

        return next_run()


class StubSource(pipe.Pipe):
    """
    Cycles through given images each time one is requested
    """
    def __init__(self, name, image_paths):
        self.name = name
        self.image_paths = image_paths

    def run(self, context, next_run):
        index = context.get('SOURCE_CURRENT_INDEX', 0)

        if index >= len(self.image_paths):
            index = 0

        current_path = self.image_paths[index]
        context['SOURCE_NAME'] = self.name
        with open(current_path, 'rb') as fh:
            context['SOURCE_RAW_CONTENT'] = fh.read()
        _, context['SOURCE_EXTENSION'] = os.path.splitext(current_path)
        context['SOURCE_DATE'] = datetime.datetime.utcnow()
        context['SOURCE_CURRENT_INDEX'] = index + 1
        return next_run()
