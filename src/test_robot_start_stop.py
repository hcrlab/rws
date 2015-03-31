import config
import json
import mock
import os
import server_factory
import tempfile
import unittest


class TestRobotStartStop(unittest.TestCase):
    def setUp(self):
        self._server = server_factory.test()

    def mock_login(self):
        """Mocks the UserVerifier so that the login check passes."""
        user = type('User', (), {'email': 'test@email.com', 'name': None})()
        self._server._user_verifier.check_user = mock.Mock(
            return_value=(user, None))
        return user

    def test_login(self):
        """Check that the robot can't be claimed without logging in."""
        pass

    def test_check(self):
        """Tests the check method in the common case."""
        self.mock_login()

        # Case 1: no one has claimed the robot.
        config.ACTIVE_USER_FILE = '/fakefile'
        rv = self._server._app.get('/api/robot/check')
        data = json.loads(rv.data)
        self.assertIsNone(data['claim'])

        # Case 2: the robot is claimed by testuser
        test_filed, test_filename = tempfile.mkstemp('test.yaml')
        with os.fdopen(test_filed, 'w') as test_file:
            config.ACTIVE_USER_FILE = test_filename
            test_file.write('user: testuser')
        rv = self._server._app.get('/api/robot/check')
        data = json.loads(rv.data)
        self.assertEquals('testuser', data['claim']['user'])


if __name__ == '__main__':
    unittest.main()
