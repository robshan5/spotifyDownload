import os

import spotipy
import yt_dlp
from spotipy.oauth2 import SpotifyOAuth
from youtubesearchpython import VideosSearch

#client ID
print("Enter client_ID: ", end="")
CLIENT_ID = input()

#client secret
print("Enter client_secret: ", end="")
CLIENT_SECRET = input()
REDIRECT_URI = "http://localhost:8888/callback"

#Playlist ID
print("Enter playlist ID: ", end="")
PLAYLIST_ID = "3QiuCZiJPD1ueeaPqW3g1p"

# Scope needed to read private playlists
SCOPE = "playlist-read-private playlist-read-collaborative"

#Playlist name
print("Enter playlist name: ", end="")
OUTPUT_DIR = "jim_playlist"

### SPOTIFY ###

# Set up authorization
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )
)


# Fetch playlist tracks
def get_playlist_tracks(sp, playlist_id):
    results = []
    offset = 0
    while True:
        response = sp.playlist_items(
            playlist_id,
            offset=offset,
            fields="items.track.name,items.track.artists.name,items.track.id,total,next",
            additional_types=["track"],
        )
        if not response["items"]:
            break
        for item in response["items"]:
            track = item["track"]
            if track:
                track_name = track["name"]
                artists = ", ".join([artist["name"] for artist in track["artists"]])
                results.append(f"{track_name} by {artists}")
        offset += len(response["items"])
        if response["next"] is None:
            break
    return results


tracks = get_playlist_tracks(sp, PLAYLIST_ID)
songs = []

# Print the track list
for i, track in enumerate(tracks, 1):
    print(f"{i}. {track}")
    songs.append(track)


### YOUTUBE PART ###

# Make output folder for songs
os.makedirs(OUTPUT_DIR, exist_ok=True)


# search the song
def search_youtube(query):
    try:
        search = VideosSearch(query, limit=1)
        result = search.result()
        if result and "result" in result and result["result"]:
            return result["result"][0]["link"]
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
    return None


# download the audio
def download_audio(youtube_url, output_path):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])


for song in songs:
    print(f"Searching for: {song}")
    # using + (audo) so we just download audio
    video_url = search_youtube(song + " (audio)")
    if video_url:
        print(f"Downloading: {video_url}")
        filename = f"{song.replace('/', '_')}"
        output_path = os.path.join(OUTPUT_DIR, filename)
        download_audio(video_url, output_path)
    else:
        print(f"No results found for: {song}")
