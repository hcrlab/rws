#!/usr/bin/env python

import server_factory

server = server_factory.production()
app = server._app
