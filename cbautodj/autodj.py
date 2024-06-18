import logging
from spotipy import Spotify, SpotifyOAuth, SpotifyException

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
        try:
            token_info = sp_oauth.get_access_token()
            access_token = token_info['access_token']
            self.spotify = Spotify(auth=access_token)
        except SpotifyException as e:
            logger.exception("Spotify authentication failed", exc_info=e)
            raise

    def check_active_devices(self):
        try:
            devices = self.spotify.devices()
            for device in devices['devices']:
                logger.debug(f"device: {device}")
                if device['is_active']:
                    logger.debug("Active!")
                    return True
            return False
        except SpotifyException as e:
            logger.exception("Failed to check active devices", exc_info=e)
            return False

    def find_song(self, song_info):
        """Add the song title to the Spotify playback queue."""
        try:
            results = self.spotify.search(q=f"{song_info['artist']} - {song_info['song']}", type='track', limit=1)
            logger.debug(f'results: {results}')
            return results
        except SpotifyException as e:
            logger.exception("Failed to find song", exc_info=e)
            return None

    def add_song_to_queue(self, track_uri):
        try:
            self.spotify.add_to_queue(track_uri)
            return True
        except SpotifyException as e:
            logger.exception("Failed to add song to queue", exc_info=e)
            return False
