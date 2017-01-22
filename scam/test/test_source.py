import httmock
import unittest
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


