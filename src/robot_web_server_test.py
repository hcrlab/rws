import apps
import mock
import server_factory
import unittest
import users


class TestRobotWebServer(unittest.TestCase):
    def setUp(self):
        self._server = server_factory.test()

    def mock_login(self):
        """Mocks the UserVerifier so that the login check passes."""
        user = type('User', (), {'email': 'test@email.com', 'name': None})()
        self._server._user_verifier.check_user = mock.Mock(
            return_value=(user, None))
        return user

    def test_run(self):
        """Check that the Flask app and the Websocket server are run."""
        self._server._app.run = mock.Mock()
        self._server._websocket_server.launch = mock.Mock()
        self._server.run(host='testhost', port='1234', debug=True)
        self._server._app.run.assert_called_with(host='testhost',
                                                 port='1234',
                                                 debug=True)
        self._server._websocket_server.launch.assert_called_with()

    def test_login_index(self):
        """Check that login is required for the home page."""
        self._server._user_verifier.check_user = mock.Mock(
            return_value=(None, users.UserVerifierError.NO_COOKIE))
        rv = self._server._app.get('/')
        self.assertTrue('Apps' not in rv.get_data())
        user = self.mock_login()
        rv = self._server._app.get('/')
        self.assertTrue(user.email in rv.get_data())

    def test_invalid_app(self):
        """Check that a 404 is returned for invalid app names."""
        self.mock_login()
        rv = self._server._app.get('/app/testapp')
        self.assertEqual(404, rv.status_code)
        rv = self._server._app.get('/app/close/testapp')
        self.assertEqual(404, rv.status_code)

    @mock.patch('apps.App')
    def test_app_launch(self, App):
        """Check that apps are launched in the common case."""
        self.mock_login()
        test_app = App('/path/to/test_app')
        self._server._rws_apps = {'test_app': test_app}
        rv = self._server._app.get('/app/test_app')
        self.assertEqual(200, rv.status_code)
        test_app.launch.assert_called_with()

    @mock.patch('apps.App')
    def test_app_close(self, App):
        """Check that apps are terminated iff they are running."""
        self.mock_login()
        test_app = App('/path/to/test_app')
        self._server._rws_apps = {'test_app': test_app}

        # If app isn't running, don't call terminate()
        test_app.is_running = mock.Mock(return_value=False)
        rv = self._server._app.get('/app/close/test_app')
        self.assertFalse(test_app.terminate.called)

        # Otherwise, call terminate()
        test_app.is_running = mock.Mock(return_value=True)
        rv = self._server._app.get('/app/close/test_app')
        self.assertTrue(test_app.terminate.called)


if __name__ == '__main__':
    unittest.main()
