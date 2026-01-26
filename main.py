import base64
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from turtle import resetscreen

import requests

import config


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        code = params.get("code")
        authorization = base64.b64encode(
            f"{config.CLIENT_ID}:{config.CLIENT_SECRET}".encode()
        ).decode()

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {authorization}",
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.REDIRECT_URI,
        }

        response = requests.post(url, headers=headers, data=data).json()
        config.ACCESS_TOKEN = response.get("access_token")
        config.REFRESH_TOKEN = response.get("refresh_token")
        update_config("ACCESS_TOKEN", 'ACCESS_TOKEN = "' + config.ACCESS_TOKEN + '"')
        update_config("REFRESH_TOKEN", 'REFRESH_TOKEN = "' + config.REFRESH_TOKEN + '"')

        exit()


def login():
    server = HTTPServer((config.HOST, config.PORT), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    params = {
        "response_type": "code",
        "client_id": config.CLIENT_ID,
        "scope": config.SCOPE,
        "redirect_uri": config.REDIRECT_URI,
    }
    webbrowser.open(
        f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    )
    thread.join()
    server.server_close()


def update_config(old_pattern, new_pattern):
    with open(config.CONFIG_FILE, "r") as f:
        lines = f.readlines()
    with open(config.CONFIG_FILE, "w") as f:
        for line in lines:
            if old_pattern in line:
                f.write(new_pattern + "\n")
            else:
                f.write(line)


def refresh_access_token():
    authorization = base64.b64encode(
        f"{config.CLIENT_ID}:{config.CLIENT_SECRET}".encode()
    ).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {authorization}",
    }
    params = {
        "grant_type": "refresh_token",
        "refresh_token": config.REFRESH_TOKEN,
        "client_id": config.CLIENT_ID,
    }
    url = (
        "https://accounts.spotify.com/api/token" + "?" + urllib.parse.urlencode(params)
    )
    response = requests.post(url, headers=headers).json()
    config.ACCESS_TOKEN = response.get("access_token")
    update_config("ACCESS_TOKEN", 'ACCESS_TOKEN = "' + config.ACCESS_TOKEN + '"')
    if "refresh_token" in response:
        config.REFRESH_TOKEN = response.get("refresh_token")
        update_config("REFRESH_TOKEN", 'REFRESH_TOKEN = "' + config.REFRESH_TOKEN + '"')


def get_api(endpoint):
    url = config.BASE_URL + endpoint
    headers = {"Authorization": f"Bearer {config.ACCESS_TOKEN}"}
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        refresh_access_token()
        return get_api(endpoint)
    else:
        print(response.content.decode())
        return False


def put_api(endpoint, params):
    url = config.BASE_URL + endpoint + "?" + urllib.parse.urlencode(params)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.ACCESS_TOKEN}",
    }
    response = requests.put(url=url, headers=headers)
    if response.status_code == 200:
        return True
    elif response.status_code == 401:
        refresh_access_token()
        return put_api(endpoint, params)
    else:
        print(response.content.decode())
        return False


def save_current_track():
    result = get_api("/me/player/currently-playing")
    if not result:
        return
    params = {
        "ids": result.get("item").get("id"),
    }
    put_api("/me/tracks", params)


def switch_repeat_state():
    result = get_api("/me/player")
    if not result:
        return
    old_repeat_state = result.get("repeat_state")
    if old_repeat_state == "off":
        new_repeat_state = "context"
    elif old_repeat_state == "context":
        new_repeat_state = "track"
    else:
        new_repeat_state = "off"
    params = {
        "state": new_repeat_state,
    }
    put_api("/me/player/repeat", params)


def switch_shuffle_state():
    result = get_api("/me/player")
    if not result:
        return
    params = {
        "state": not result.get("shuffle_state"),
    }
    put_api("/me/player/shuffle", params)


def toggle_play_pause():
    result = get_api("/me/player")
    if not result:
        return
    is_playing = result.get("is_playing")
    if is_playing:
        put_api("/me/player/pause", {})
    else:
        put_api("/me/player/play", {})


def change_volume(step):
    result = get_api("/me/player")
    if not result:
        return
    volume = result.get("device").get("volume_percent")
    params = {"volume_percent": max(min(volume + step, 100), 0)}
    put_api("/me/player/volume", params)


if __name__ == "__main__":
    if config.REFRESH_TOKEN == "" and config.ACCESS_TOKEN == "":
        login()
    if len(sys.argv) > 1:
        match sys.argv[1]:
            case "play_pause":
                toggle_play_pause()
            case "save":
                save_current_track()
            case "repeat":
                switch_repeat_state()
            case "shuffle":
                switch_shuffle_state()
            case "volume_up":
                change_volume(+5)
            case "volume_down":
                change_volume(-5)
