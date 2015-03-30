# The protocol, server, and port we are serving this site under.
SERVER_ORIGIN = 'localhost:5000'
WEBSOCKET_URL = 'ws://localhost:9999'

# Not really a secret, but it's probably better to leave it out of source
# control. API key for the OAuth 2 callback.
BROWSER_API_KEY = 'AIza...'

GITKIT_SERVER_CONFIG_PATH = '../resources/gitkit/gitkit-server-config.json'

# List of users allowed to log in.
ALLOWED_USERS = ['example@example.com', ]

CATKIN_WS = '/home/rosie/rws/catkin_ws'
