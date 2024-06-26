import logging
import openai

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SongExtractor:
    def __init__(self, api_key):
        self.openai_client = openai.OpenAI(api_key=api_key)

    def find_titles(self, message, song_count=1):
        """Use OpenAI GPT-4 to extract song titles from the message."""
        try:
            response = self.openai_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a bot designed to identify song titles in input text and reply with a json object containing the artist and title of the song. If more than 1 song is requested from the input text, return a list of json objects."
                    },
                    {
                        "role": "user",
                        "content": f"""Extract exactly {song_count} song title{"s" if song_count > 1 else ""} from the following message. Provide the response as a | separated list without any other unrelated text. The format should resemble "Artist--Song Title|Artist--Song Title|...". Each entry should be exactly in the format 'Artist--Song Title' with '|' separating multiple entries:

                        {message}"""
                    }
                ],
                model="gpt-4o"
            )

            song_titles_response = response.choices[0].message.content.strip().split('|')
            song_titles = []
            for idx, resp in enumerate(song_titles_response):
                if '--' in resp:
                    artist, song = resp.split('--', 1)
                    song_titles.append(
                        {
                            "artist": artist.strip(),
                            "song": song.strip(),
                            "gpt": True
                        }
                    )
                else:
                    logger.warning(f"Unexpected format in response: {resp}")
                    #if len(song_titles_response) == 1 and song_count == 1:
                    if song_count == 1:
                        logger.warning("Returning original request to attempt Spotify query.")
                        song_titles.append(
                            {
                                "artist": "",
                                "song": message,
                                "gpt": False
                            }
                        )

            logger.debug(f'song_titles: {song_titles}')
            logger.debug(f"len(song_titles): {len(song_titles)}")

            return song_titles

        except openai.APIError as e:
            logger.exception("Failed to extract song titles", exc_info=e)
            return []
