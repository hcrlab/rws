import os
import subprocess


# TODO(jstn): If there are enough classes like these that duplicate roslaunch
# functionality (see App), then make a separate Launcher class.
class WebsocketServer(object):
    """Websocket server launcher.
    
    Example usage:
    ws = WebsocketServer(9999)
    ws.launch()
    ...
    ws.is_running()
    ...
    ws.terminate()
    """

    def __init__(self, port):
        self._port = port
        self._subprocess = None

    def port(self):
        return self._port

    def is_running(self):
        return self._subprocess is not None

    def launch(self):
        if self._subprocess is None:
            self._subprocess = subprocess.Popen(
                ['roslaunch', 'rosbridge_server', 'rosbridge_websocket.launch',
                 'port:={}'.format(self._port)],
                env=os.environ)

    def terminate(self):
        self._subprocess.terminate()
        self._subprocess.wait()
        self._subprocess = None
