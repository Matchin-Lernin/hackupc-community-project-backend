#!flask/bin/python
from flask import Flask, jsonify
import requests
import pyrebase
import re
import kmeans
import json

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

access_token='BQCXkjJzTIGTrcCeWM4GEfPpXjzuXUT-ARSOKe1f8yaK3cf-WWIvkmPlukKmhGMGppjV6G78GzZ6BHRv63WL6wWlRUM1GdnGXL4DyHqWhviU8H05NX099zViUHkCj9eNNKVwDlCf-A_7J3jREJ_s-35hP3H61p32DztZ8vVSnrDTX0bWu6yequER2pmjmoRjxb345z0XyNzQQ-w78I752SW3YkrwPuuej1r4AwNoaLZmQrByG5xaqkM-7XlLaZpkyI6vryfKpM8'
firebase = pyrebase.initialize_app(config)

db = firebase.database()
local = {}
kmeans_instance = kmeans.KMeansMethod()
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/exit/<id_user>/<id_local>/')
def exit(id_user, id_local):
    users = db.child("playlists").child(id_local).get().val()
    # print(type(users))
    users.remove(id_user)
    print(users)
    try:
        db.child("playlists").child(id_local).set(users)
    except _ as _:
        print("Child is already out(?)")
    db.child("users").child(id_user).remove()
    # TODO jordi kmeans.get(list(user)); local[id_local] = result;
    return str(users)

#TODO @sergi add add_tracks_to_playlist in add and delete functions

@app.route('/add/<id_user>/<id_local>/<songs>/')
def add(id_user, id_local, songs):
    users = db.child("playlists").child(id_local).get().val()
    users.append(id_user)
    users = set(users)
    users = list(users)
    db.child("playlists").child(id_local).set(users)
    user_songs = list(filter( lambda x: x is not None,[get_id_song_from_string(song) for song in songs.split(',')]))
    add_music(id_user, user_songs)
    feature_lists = get_features_from_songs(user_songs)
    features_df = kmeans_instance.list_to_dataFrame(feature_lists)
    recomendations = kmeans_instance.recommend(features_df)
    remove_track_from_playlist(id_local)
    add_tracks_to_playlist(id_local, recomendations)
    return str(users)

def get_playlist_tracks(id_local):
    header = {'Authorization': f'Bearer {access_token}'}
    endpoint = f'https://api.spotify.com/v1/playlists/{id_local}/tracks?market=ES&fields=items(track(uri))' 
    track_response = requests.get(endpoint, headers=header, params={'playlist_id':id_local},timeout=SPOTIFY_API_TIMEOUT)
    if track_response.ok:
        tracks = list()
        for item in track_response.json()['items']:
            tracks.append({'uri':item['track']['uri']})
        dicc  = {'tracks':tracks}
        return dicc
    return None

def remove_track_from_playlist(id_local):
    header = {'Authorization': f'Bearer {access_token}'}
    endpoint = f'https://api.spotify.com/v1/playlists/{id_local}/tracks' 
    playlist_tracks = get_playlist_tracks(id_local)
    request = requests.delete(endpoint, headers=header, data=json.dumps(playlist_tracks), timeout=SPOTIFY_API_TIMEOUT)
    if request.ok:
        print("Content deleted successfully")
    else:
        print("Error removing the content")

def add_music(id_local, user_songs):
    db.child("users").child(id_local).set(user_songs)
    # print(db.child("users").child(id_local).get().val())

def get_id_song_from_string(song):
    for _ in range(0, SPOTIFY_API_RETRIES):
        headers = {'Authorization': f'Bearer {access_token}'}
        endpoint = 'https://api.spotify.com/v1/search'
        # TODO: DELETE SONGS FROM PLAYLIST
        track_response = requests.get(endpoint, headers=headers, params={'q':song,'type':'track'},timeout=SPOTIFY_API_TIMEOUT) 
        print(track_response)
        if track_response.ok:
            m = re.search(r'track/(.*)"', track_response.text)
            print('GOD TO C U')
            print(m)
            return None if m is None else m.group(1)
    print("esta feo")
    return None

def get_features_from_songs(songs_list_ids):
    headers = {'Authorization': f'Bearer {access_token}'}
    endpoint = 'https://api.spotify.com/v1/audio-features'
    track_features = requests.get(endpoint, headers=headers, params={'ids':songs_list_ids}, timeout=SPOTIFY_API_TIMEOUT)
    if track_features.ok:
        features_list = parse_features(track_features.json())
        return None if features_list is None else features_list

    return None

def parse_features(json_features_list):
    csv_features = list()
    for feature in json_features_list['audio_features']:
        csv_feature = list()
        csv_feature.append(feature['danceability'])
        csv_feature.append(feature['energy'])
        csv_feature.append(feature['key'])
        csv_feature.append(feature['loudness'])
        csv_feature.append(feature['mode'])
        csv_feature.append(feature['speechiness'])
        csv_feature.append(feature['acousticness'])
        csv_feature.append(feature['instrumentalness'])
        csv_feature.append(feature['liveness'])
        csv_feature.append(feature['valence'])
        csv_feature.append(feature['tempo'])
        csv_features.append(csv_feature)
    
    return csv_features if csv_features else None

def add_tracks_to_playlist(id_local, track_uri_list):
    songs = list()
    for user in db.child("users").get().each():
        songs.extend(user.val())
    print(songs)
    for _ in range(0, SPOTIFY_API_RETRIES):
        headers = {'Authorization': f'Bearer {access_token}'}
        data = {'uris': track_uri_list}
        endpoint = SPOTIFY_API_ADD_TRACKS.format(playlist_id=id_local)
        # TODO: DELETE SONGS FROM PLAYLIST
        track_response = requests.post(endpoint, json=data, headers=headers, timeout=SPOTIFY_API_TIMEOUT)
        if track_response.ok:
            return True
    return None

if __name__ == '__main__':
    app.run(debug=True)
