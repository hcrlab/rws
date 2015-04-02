#!/usr/bin/env python

"""Production server launch file.

In production, RWS runs on Apache with mod_wsgi, so we need to do our
initialization at the top level and expose the Flask application.
"""

import server_factory

server = server_factory.production()
server._websocket_server.launch()
app = server._app
