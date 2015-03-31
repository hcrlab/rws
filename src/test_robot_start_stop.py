import config
import json
import mock
import os
import server_factory
import subprocess
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
        rv = self._server._app.get('/api/robot/check')
        self.assertTrue('Log in' in rv.data)

        self.mock_login()
        rv = self._server._app.get('/api/robot/check')
        self.assertFalse('Log in' in rv.data)

    def test_claim(self):
        """Check that the claim endpoint works in the common case."""
        self.mock_login()

        subprocess.check_call = mock.Mock()
        rv = self._server._app.post('/api/robot/claim',
                                    data={'user': 'test@email.com'})
        subprocess.check_call.assert_called_with(
            'robot claim -f --username test@email.com --email test@email.com -m "Claimed via Robot Web Server"',
            shell=True)

    def test_start(self):
        """Check that the start endpoint works in the common case."""
        self.mock_login()

        subprocess.check_call = mock.Mock()
        rv = self._server._app.post('/api/robot/start')
        subprocess.check_call.assert_called_with('robot start -f', shell=True)

    def test_stop(self):
        """Check that the stop endpoint works in the common case."""
        self.mock_login()

        subprocess.check_call = mock.Mock()
        rv = self._server._app.post('/api/robot/stop')
        subprocess.check_call.assert_called_with('robot stop -f', shell=True)

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
