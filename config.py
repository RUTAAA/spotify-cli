CONFIG_FILE = "config.py"

CLIENT_ID = ""
CLIENT_SECRET = ""

PROTOCOL = ""
HOST = ""
PORT = 0
ENDPOINT = ""
REDIRECT_URI = f"{PROTOCOL}://{HOST}:{PORT}{ENDPOINT}"

SCOPE = "user-read-currently-playing user-read-playback-state user-modify-playback-state user-library-modify"
REFRESH_TOKEN = ""
ACCESS_TOKEN = ""

BASE_URL = "https://api.spotify.com/v1"
