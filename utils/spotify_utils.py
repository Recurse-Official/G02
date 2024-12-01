import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

def initialize_spotify():
    spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if spotify_client_id and spotify_client_secret:
        return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret
        ))
    return None

def fetch_spotify_songs(mood):
    sp = initialize_spotify()
    if not sp:
        return []
    try:
        search_results = sp.search(q=mood, type="playlist", limit=1)
        playlist_id = search_results["playlists"]["items"][0]["id"]
        playlist_tracks = sp.playlist_tracks(playlist_id)
        return [
            {
                "name": track["track"]["name"],
                "artist": track["track"]["artists"][0]["name"],
                "url": track["track"]["external_urls"]["spotify"]
            }
            for track in playlist_tracks["items"]
        ][:5]
    except Exception:
        return []
