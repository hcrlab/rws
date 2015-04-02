#!/usr/bin/env python

import argparse
import server_factory

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Robot web server.')
    parser.add_argument('--debug',
                        type=bool,
                        default=False,
                        help='Whether to start the server in debug mode.')
    args = parser.parse_args()
    server = server_factory.development()
    server._websocket_server.launch()
    server._app.run(host='0.0.0.0', debug=args.debug)
