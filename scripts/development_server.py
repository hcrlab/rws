#!/usr/bin/env python

import argparse
import rospy
from rws import server_factory

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Robot web server.')
    parser.add_argument('--debug',
                        type=bool,
                        default=False,
                        help='Whether to start the server in debug mode.')
    args = parser.parse_args(args=rospy.myargv()[1:])
    server = server_factory.development()
    server._app.run(host='0.0.0.0', port=5001, debug=args.debug)
