import configparser
import logging
import os
import queue
import threading
import time
from logging.handlers import RotatingFileHandler

import requests
from requests.exceptions import RequestException

from cbautodj.autodj import AutoDJ
from cbautodj.songextractor import SongExtractor

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")

log_file = config.get("Logging", "log_file")
log_max_size_mb = config.getint("Logging", "log_max_size_mb")
log_backup_count = config.getint("Logging", "log_backup_count")

if not os.path.exists(os.path.dirname(log_file)):
    os.makedirs(os.path.dirname(log_file))

# Load configuration and setup logging (same as before)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
stream_handler = logging.StreamHandler()
file_handler = RotatingFileHandler(
    log_file, maxBytes=log_max_size_mb * 1024 * 1024, backupCount=log_backup_count  # type: ignore
)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

events_api_url = config.get("Events API", "url")
requests_per_minute = config.getint("Events API", "max_requests_per_minute")

# Set your OpenAI API key
openai_api_key = config.get('OpenAI', 'api_key')

# Spotify credentials
spotify_client_id = config.get('Spotify', 'client_id')
spotify_client_secret = config.get('Spotify', 'client_secret')
spotify_redirect_uri = config.get('Spotify', 'redirect_url')

# General Settings
tip_multiple = config.getint('General', 'tip_multiple')

# Initialize Clients and Controllers
auto_dj = AutoDJ(
    client_id=spotify_client_id,
    client_secret=spotify_client_secret,
    redirect_uri=spotify_redirect_uri
)
song_extractor = SongExtractor(openai_api_key)

event_queue = queue.Queue()
stop_event = threading.Event()


def process_event(event):
    """
    Process the event from the queue.
    """
    # Implement event processing logic here
    logger.debug(f"process_event: {event}")

    event_method = event["method"]
    logger.debug(f"event_method: {event_method}")
    event_object = event["object"]
    logger.debug(f"event_object: {event_object}")

    if event_method == "tip":
        print("TIP")

        tip_amount = event_object["tip"]["tokens"]
        logger.debug(f"tip_amount: {tip_amount}")

        if tip_amount and tip_amount % tip_multiple == 0:
            tip_message = event_object["tip"]["message"]
            logger.debug(f"tip_message: {tip_message}")

            song_count = tip_amount / tip_multiple
            logger.debug("song_count: {song_count}")

            # NEED TO MODIFY TO HANDLE MULTIPLE SONG EVENT
            title_results = song_extractor.find_titles(message=tip_message, song_count=song_count)
            logger.debug(f'title_results: {title_results}')

            if title_results:
                for result in title_results:
                    logger.info(f"Artist: {result['artist']}")
                    logger.info(f"Song: {result['song']}")
                    auto_dj.add_song_to_playlist(result)

    elif event_method == "mediaPurchase":
        print("MEDIA PURCHASE")

    elif event_method == "follow":
        print("FOLLOW")

    elif event_method == "chatMessage":
        print("CHAT MESSAGE")


def event_processor(stop_event):
    """
    Continuously process events from the event queue.
    """
    while not stop_event.is_set():
        try:
            event = event_queue.get(timeout=1)  # Timeout to check for stop signal
            process_event(event)
            event_queue.task_done()
        except queue.Empty:
            continue  # Resume loop if no event and check for stop signal


def long_polling(url, interval, stop_event):
    """
    Continuously poll the API and put events into the queue.
    """
    url_next = url

    while not stop_event.is_set():
        try:
            response = requests.get(url_next)
            if response.status_code == 200:
                data = response.json()
                for event in data["events"]:
                    event_queue.put(event)
                url_next = data["nextUrl"]
            else:
                logger.error(f"Error: Received status code {response.status_code}")
        except RequestException as e:
            logger.error(f"Request failed: {e}")

        time.sleep(interval)


if __name__ == "__main__":
    interval = 60 / (requests_per_minute / 10)  # type: ignore

    # Start the event processor thread
    processor_thread = threading.Thread(
        target=event_processor, args=(stop_event,), daemon=True
    )
    processor_thread.start()

    try:
        long_polling(events_api_url, interval, stop_event)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Cleaning up...")
        #obs_controller.cleanup()
        stop_event.set()
        processor_thread.join()
        print("Done.")
