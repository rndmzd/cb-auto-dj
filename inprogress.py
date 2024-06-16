import configparser
import requests
import json
import logging
import time
import openai
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from cbautodj.autodj import AutoDJ
from cbautodj.songextractor import SongExtractor

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config_path = './config.ini'

config = configparser.RawConfigParser()
config.read(config_path)

# Set your OpenAI API key
#openai.api_key = config.get('OpenAI', 'api_key')
openai_api_key = config.get('Open AI', 'api_key')

# Spotify credentials
spotify_client_id = config.get('Spotify', 'client_id')
spotify_client_secret = config.get('Spotify', 'client_secret')
spotify_redirect_uri = config.get('Spotify', 'redirect_url')
spotify_access_token = config.get('Spotify', 'access_token')

# Initialize Spotify client
auto_dj = AutoDJ(spotify_access_token)
song_extractor = SongExtractor(openai_api_key)

def monitor_api(url):
    """Monitor the API for incoming events."""
    while True:
        response = requests.get(url)
        events = response.json()
        for event in events:
            handle_event(event)
        time.sleep(5)  # Adjust the polling interval as needed

def handle_event(event):
    """Handle the incoming event."""
    if event.get('type') == 'token_tipping':
        amount = event.get('amount')
        if amount and amount % 27 == 0:
            message = event.get('message')
            if message:
                process_message(message)

def process_message(message):
    """Process the message to find song titles and add them to Spotify queue."""
    song_titles = song_extractor.find_titles(message)
    for result in song_titles:
        logger.info(f"Artist: {result['artist']}")
        logger.info(f"Song: {result['song']}")
        auto_dj.add_song_to_playlist(result)

# Start monitoring the API
api_url = 'your_api_url'  # Replace with the actual API URL
monitor_api(api_url)
