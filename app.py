#!flask/bin/python
from flask import Flask, jsonify
import requests
import pyrebase

SPOTIFY_API_RETRIES = 3
SPOTIFY_API_RTD = 5
SPOTIFY_API_TIMEOUT = 15
SPOTIFY_RESPONSE_TYPE = 'code'
SPOTIFY_REDIRECT_URI = 'https://gitinspect.ml/'
SPOTIFY_SCOPES = 'playlist-modify-private playlist-modify-public'
SPOTIFY_API_ADD_TRACKS = 'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

MESSAGE_ERROR = 'Unexpected error.'
MESSAGE_USER_NOT_FOUND = 'User not found.'
MESSAGE_REPOS_NOT_FOUND = 'You should have at least one public repository.'
MESSAGE_TOKEN_NOT_FOUND = 'Error while retrieving the Spotify token.'
MESSAGE_SPOTIFY_NOT_FOUND = 'Spotify user not found.'
MESSAGE_SPOTIFY_PLAYLIST_ERROR = 'Spotify playlist cannot be created.'
MESSAGE_COMMIT_NOT_FOUND = 'Any commit could be retrieved.'
MESSAGE_SPOTIFY_TRACK_ERROR = 'Spotify tracks cannot be created.'

config = {
    "apiKey": "AIzaSyB8VcTw2-4pUZ7Aulgk7HDPrJu_YqmvLwA",
    "authDomain": "hackeps-matchin-lernin.firebaseapp.com",
    "databaseURL": "https://hackeps-matchin-lernin.firebaseio.com",
    "storageBucket": "hackeps-matchin-lernin.appspot.com"
    # messagingSenderId: "410445493149",
    # appId: "1:410445493149:web:475bfdfdac4df417173574",
    # measurementId: "G-287LP5C3VX"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()
local = {}

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/exit/<id_user>/<id_local>')
def exit(id_user, id_local):
    users = db.child("playlists").child(id_local).get().val()
    # print(type(users))
    users.remove(id_user)
    db.child("playlists").child(id_local).set(users)
    user_set = set()
    for user in db.child("users").get().each():
        user_set.add(user.val())
    # TODO jordi kmeans.get(list(user)); local[id_local] = result;

    return str(users)

#TODO @sergi add add_tracks_to_playlist in add and delete functions

@app.route('/add/<id_user>/<id_local>')
def add(id_user, id_local):
    users = db.child("playlists").child(id_local).get().val()
    # print(type(users))
    users.append(id_user)
    db.child("playlists").child(id_local).set(users)
    return str(users)


def add_tracks_to_playlist(playlist_id, track_uri_list):
    access_token='asdf'
    for _ in range(0, SPOTIFY_API_RETRIES):
        headers = {'Authorization': f'Bearer {access_token}'}
        data = {'uris': track_uri_list}
        endpoint = SPOTIFY_API_ADD_TRACKS.format(playlist_id=playlist_id)
        # TODO: DELETE SONGS FROM PLAYLIST
        track_response = requests.post(endpoint, json=data, headers=headers, timeout=SPOTIFY_API_TIMEOUT)
        if track_response.ok:
            return True

    return None

if __name__ == '__main__':
    app.run(debug=True)
