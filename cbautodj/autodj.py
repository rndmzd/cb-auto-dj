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

        # Get and set playback device
        try:
            spotify_devices = self.spotify.devices()
            print("==[ Available Spotify Devices ]==\n")
            for idx, device in enumerate(spotify_devices):
                print(f"{idx+1} - {device['name']}\n")

            while True:
                user_selection = int(input("Choose playback device: "))
                logger.debug(f"user_selection: {user_selection}")

                if user_selection not in range(0, len(spotify_devices)-1):
                    logger.error("Invalid device number. Try again.")
                    continue

                self.playback_device = spotify_devices[user_selection-1]["id"]
                break
        except Exception as e:
            logger.exception("Spotify playback device selection failed", exc_info=e)
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
    
    def get_device_info(self, device_id):
        try:
            for device in self.spotify.devices():
                if device['id'] == device_id:
                    return device
            else:
                logger.warning("Could not find device with provided id.")
                return None
        except Exception as e:
            logger.exception("Failed to retrieve device information.", exc_info=e)

    def add_song_to_queue(self, track_uri):
        try:
            if self.get_device_info(device_id=self.playback_device)['is_active'] is False:
                logger.info("Playback device inactive. Transferring playback to device.")
                self.spotify.transfer_playback(device_id=self.playback_device)

            logger.info("Adding song to active playback queue.")
            self.spotify.add_to_queue(track_uri, device_id=self.playback_device)
            
            playback_state = self.spotify.current_playback()
            logger.debug(f"playback_state: {playback_state}")

            if playback_state["is_playing"] is False:
                self.spotify.start_playback(device_id=self.playback_device)

            """if len(self.spotify.queue()) == 0:
                logger.info("No song in active playback. Starting playback with requested song.")
                self.spotify.start_playback(device_id=self.playback_device, uris=[track_uri])
            else:
                logger.info("Adding song to active playback queue.")
                self.spotify.add_to_queue(track_uri, device_id=self.playback_device)"""
            
            return True
        except SpotifyException as e:
            logger.exception("Failed to add song to queue", exc_info=e)
            return False
