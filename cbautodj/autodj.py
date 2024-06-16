import logging
from spotipy import Spotify, SpotifyOAuth

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AutoDJ:

    def __init__(self, client_id, client_secret, redirect_uri):
        # Initialize Spotify OAuth
        sp_oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-modify-playback-state user-read-playback-state"
        )

        # Get access token
        token_info = sp_oauth.get_access_token()
        access_token = token_info['access_token']
        self.spotify = Spotify(auth=access_token)
    
    def check_active_devices(self):
        devices = self.spotify.devices()
        for device in devices['devices']:
            logger.debug(f"device: {device}")
            if device['is_active']:
                logger.debug("Active!")
                return True
        return False

    def find_song(self, song_info):
        """Add the song title to the Spotify playback queue."""
        results = self.spotify.search(q=f"{song_info['artist']} - {song_info['song']}", type='track', limit=1)
        logger.debug(f'results: {results}')
        return results
    
    def add_song_to_queue(self, track_uri):
        try:
            self.spotify.add_to_queue(track_uri)
            return True
        except Exception as e:
            logger.exception(e)
            return False