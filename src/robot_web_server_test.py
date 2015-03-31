import mock
import server_factory
import unittest
import users


class TestRobotWebServer(unittest.TestCase):
    def setUp(self):
        self._server = server_factory.test()

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
        user = type('User', (), {'email': 'test@email.com', 'name': None})()
        self._server._user_verifier.check_user = mock.Mock(
            return_value=(user, None))
        rv = self._server._app.get('/')
        self.assertTrue(user.email in rv.get_data())

    def test_invalid_app(self):
        """Check that a 404 is returned for invalid app names."""
        user = type('User', (), {'email': 'test@email.com', 'name': None})()
        self._server._user_verifier.check_user = mock.Mock(
            return_value=(user, None))
        rv = self._server._app.get('/app/testapp')
        self.assertEqual(404, rv.status_code)
        rv = self._server._app.get('/app/close/testapp')
        self.assertEqual(404, rv.status_code)


if __name__ == '__main__':
    unittest.main()
