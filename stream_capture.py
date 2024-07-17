import os
import requests
import shutil
from datetime import datetime, timedelta
import logging


def download_audio_chunk(url: str, duration: int, chunk_size: int = 1024, in_process_recording_directory: str = "recordings/in_progress", completed_recording_directory: str = "recordings/completed") -> None:
    """
    Downloads a chunk of audio from a given URL and stores it in a specified directory.

    This function streams audio from the specified URL for a given duration,
    saves the streamed audio as a chunk in an 'in progress' directory, and then
    moves the completed audio file to a 'completed' directory.

    Parameters:
    - url (str): The URL of the audio stream.
    - duration (int): The duration for which to download the stream (in seconds).
    - chunk_size (int): The size of chunks to read in bytes (default 1024).
    - in_process_recording_directory (str): The directory to temporarily store the downloading audio chunk.
    - completed_recording_directory (str): The directory to store the audio chunk once download is complete.
    - log_file (str): The file to which logs will be written.

    Returns:
    None
    """
    # Validate parameters
    if not isinstance(url, str) or not url:
        raise ValueError("URL must be a non-empty string")
    if not isinstance(duration, int) or duration <= 0:
        raise ValueError("Duration must be a positive integer")
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("Chunk size must be a positive integer")

    # Create the directories if they don't exist
    os.makedirs(in_process_recording_directory, exist_ok=True)
    os.makedirs(completed_recording_directory, exist_ok=True)

    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    in_process_filepath = os.path.join(in_process_recording_directory, filename)

    logger = logging.getLogger(__name__)

    try:
        # Send a GET request to the audio stream URL
        logger.info(f"Starting stream capture.")
        response = requests.get(url, stream=True, timeout=duration)
        response.raise_for_status()  # Raise an exception if the status code is not 2xx

        with open(in_process_filepath, 'wb') as fd:
            end_time = datetime.now() + timedelta(seconds=duration)
            while datetime.now() < end_time:
                chunk = response.raw.read(chunk_size)
                if not chunk:
                    break
                fd.write(chunk)

        logger.info(f"Wrote file {filename} to {in_process_recording_directory}.")

        # Move the file from in_process_directory to completed_directory
        completed_filepath = os.path.join(completed_recording_directory, filename)
        shutil.move(in_process_filepath, completed_filepath)
        logger.info(f"Moved file {filename} to {completed_recording_directory}.")

    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
    except IOError as e:
        logger.error(f"I/O error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {type(e).__name__}, {e}")


if __name__ == "__main__":
    url = 'https://18743.live.streamtheworld.com/KQMVFM.mp3?dist=hubbard&source=hubbard-web&ttag=web&gdpr=0'
    in_progress_directory = "recordings/in_progress"
    completed_directory = "recordings/completed"
    duration = 120  # seconds
    print(f"Starting audio download.")
    download_audio_chunk(url=url, duration=duration, chunk_size=1024, in_process_recording_directory=in_progress_directory, completed_recording_directory=completed_directory)
    print(f"Audio download complete.")
