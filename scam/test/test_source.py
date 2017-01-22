import httmock
import unittest
import os
from scam import source

class IpCameraTestCase(unittest.TestCase):
    def test_snapshot_success_with_basic_auth(self):
        # Arrange
        @httmock.all_requests
        def response_content(url, request):
            # Username = Aladdin, Password = OpenSesame
            if request.headers['authorization'] == 'Basic QWxhZGRpbjpPcGVuU2VzYW1l':
                return httmock.response(200, content=b'hi', headers={
                    'content-type': 'image/jpeg'
                })
            return httmock.response(401)

        camera = source.IpCamera('Test Camera', 'example.com', basic_username='Aladdin', basic_password='OpenSesame')

        # Act
        with httmock.HTTMock(response_content):
            context = {}
            camera.run(context, lambda: None)
            # Assert
            self.assertEqual(context['SOURCE_EXTENSION'], '.jpeg')
            self.assertEqual(context['SOURCE_RAW_CONTENT'], b'hi')

    def test_snapshot_fails_with_incorrect_password(self):
        # Arrange
        @httmock.all_requests
        def response_content(url, request):
            return httmock.response(401)

        camera = source.IpCamera('Test Camera', 'example.com', basic_username='Aladdin', basic_password='OpenSesame')

        # Act
        with httmock.HTTMock(response_content):
            # Assert
            with self.assertRaises(source.SnapshotError):
                snapshot = camera.run({}, lambda: None)


class StubSourceTestCase(unittest.TestCase):
    def get_test_image_path(self, name):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dir_path, 'resources', name)

    def test_success(self):
        # Arrange
        stub_source = source.StubSource('Test', [self.get_test_image_path('snapshot1.jpg'), self.get_test_image_path('snapshot2.jpg')])

        # Act
        context = {}
        stub_source.run(context, lambda: None)

        # Assert
        self.assertEqual(context['SOURCE_EXTENSION'], '.jpg')
        self.assertIn('SOURCE_RAW_CONTENT', context)
