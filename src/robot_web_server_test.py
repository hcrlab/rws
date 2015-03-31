import mock
import server_factory
import unittest


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


if __name__ == '__main__':
    unittest.main()
