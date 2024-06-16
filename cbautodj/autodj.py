import logging
from spotipy import Spotify, SpotifyOAuth

logger = logging.getLogger()


class AutoDJ:

    def __init__(self, client_id, client_secret, redirect_uri):
        # Initialize Spotify OAuth
        sp_oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-modify-playback-state"
        )

        # Get access token
        token_info = sp_oauth.get_access_token()
        access_token = token_info['access_token']
        self.spotify = Spotify(auth=access_token)

    def add_song_to_playlist(self, song_info):
        """Add the song title to the Spotify playback queue."""
        results = self.spotify.search(q=f"{song_info['artist']} - {song_info['song']}", type='track', limit=1)
        logger.debug(f'results: {results}')

        tracks = results['tracks']['items']
        if tracks:
            track_uri = tracks[0]['uri']
            logger.debug(f"track_uri: {track_uri}")
            self.spotify.add_to_queue(track_uri)
        
        return tracks