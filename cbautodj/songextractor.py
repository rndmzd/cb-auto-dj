import logging
import openai

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SongExtractor:

    def __init__(self, api_key):
        self.openai_client = openai.OpenAI(
            api_key = api_key
        )

    def find_titles(self, message, song_count=1):
        """Use OpenAI GPT-4 to extract song titles from the message."""
        response = self.openai_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""Extract exactly {song_count} song title{"s" if song_count == 1 else ""} from the following message. Provide the response as a | separated list without any other unrelated text. The format should resemble "Artist--Song Title|Artist--Song Title|...":

                    {message}"""
                }
            ],
            model="gpt-4o"
        )

        song_titles_response = response.choices[0].message.content.split('|')
        song_titles = []
        for idx, resp in enumerate(song_titles_response):
            song_titles.append(
                {
                    "artist": resp.split('--')[0],
                    "song": resp.split('--')[1]
                }
            )

        logger.debug(f'song_titles: {song_titles}')
        logger.debug(f"len(song_titles): {len(song_titles)}")

        return song_titles