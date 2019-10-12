#!flask/bin/python
from flask import Flask, jsonify
import requests
import pyrebase
import re

SPOTIFY_API_RETRIES = 3
SPOTIFY_API_RTD = 5
SPOTIFY_API_TIMEOUT = 15
SPOTIFY_RESPONSE_TYPE = 'code'
SPOTIFY_REDIRECT_URI = 'https://gitinspect.ml/'
SPOTIFY_SCOPES = 'playlist-modify-private playlist-modify-public'
SPOTIFY_API_ADD_TRACKS = 'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
SPOTIFY_SEARCH = 'https://api.spotify.com/v1/search'

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

access_token='BQAi2iOaQ-MBXqLGSdMJH1A1xmreYGBeWRGzaHHuTuwBCj9ycHjo_Te_pZzwloCKY2jDE_Ys3JS4sY55E-mYirtWRoddVkLwllAHwaA5_IwSlOPKHFJ-NT3C68InDcdWftGZNdzpEyZZARFYZDFsCSyIbonzI8Ui8ajd_NHyeUgJAXt7QeN9b1BNVh2bOcTrtTZeqoxwyejoaYV2ogAOlXsOxFNZc3J4IF64UCVkZKXyKXUjleShZV2VeGuzWCbE-N7Z6sb8wt8'
firebase = pyrebase.initialize_app(config)

db = firebase.database()
local = {}

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/exit/<id_user>/<id_local>/')
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

@app.route('/add/<id_user>/<id_local>/<songs>')
def add(id_user, id_local, songs):
    print
    users = db.child("playlists").child(id_local).get().val()
    # print(type(users))
    users.append(id_user)
    users = set(users)
    users = list(users)
    db.child("playlists").child(id_local).set(users)
    user_songs = list(filter( lambda x: x is not None,[get_id_song_from_string(song) for song in songs.split(',')]))
    add_music(id_user, user_songs)
    refresh_playlist(id_local)
    print(user_songs)
    return str(users)

def add_music(id_local, user_songs):
    db.child("users").child(id_local).set(user_songs)
    print(db.child("users").child(id_local).get().val())

def refresh_playlist(id_local):
    parametrized_data = []
    for user in db.child("playlists").child(id_local).get().each():
        tracks = db.child("users").child(user).get().val()
        print(type(tracks))
    return parametrized_data

def get_id_song_from_string(song):
    for _ in range(0, SPOTIFY_API_RETRIES):
        headers = {'Authorization': f'Bearer {access_token}'}
        endpoint = 'https://api.spotify.com/v1/search'
        # TODO: DELETE SONGS FROM PLAYLIST
        track_response = requests.get(endpoint, headers=headers, params={'q':song,'type':'track'},timeout=SPOTIFY_API_TIMEOUT) 
        print(track_response)
        if track_response.ok:
            m = re.search(r'track/(.*)', track_response.text)
            print('GOD TO C U')
            print(m)
            return None if m is None else m.group(1)
    print("esta feo")
    return None

def add_tracks_to_playlist(playlist_id, track_uri_list):
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
