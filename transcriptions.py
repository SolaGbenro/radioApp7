import logging
import os
import shutil
import time
from datetime import datetime

from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def transcribe_audio_file(model, file_path: str) -> str:
    """
    Transcribes an audio file to text using the specified Whisper model.

    Parameters:
    - model: The loaded Whisper model used for transcription.
    - file_path (str): The path to the audio file to be transcribed.

    Returns:
    - str: The transcribed text from the audio file.
    """
    # Get the logger
    logger = logging.getLogger(__name__)

    try:
        start_time = time.time()
        result = model.transcribe(file_path)
        end_time = time.time()
        transcription_time = end_time - start_time
        normalized_path = os.path.normpath(file_path)
        logger.info(f"Transcription of {normalized_path} took {transcription_time:.2f} seconds.")
        # print(f"Transcription of {normalized_path} took {transcription_time:.2f} seconds.")
        return result['text']
    except Exception as e:
        logger.error(f"An unexpected error occurred while transcribing audio file: {type(e).__name__}, {e}")


# def transcribe_and_move_audio_files(completed_recordings_directory: str = "recordings/completed", completed_transcription_directory ="transcriptions/completed") -> None:
#     """
#     Transcribes audio files from a directory and manages the transcription and audio files.
#
#     Transcribes all audio files in the completed recordings directory, saves the transcriptions
#     to a specified directory, and optionally moves audio files to an archive directory.
#
#     Parameters:
#     - completed_recordings_directory (str): Directory containing completed audio recordings.
#     - completed_transcription_directory (str): Target directory for saving transcriptions.
#
#     Returns:
#     None
#     """
#     # Choose model size
#     # model = load_model(name="base", device="cuda")  # Adjust the model size as needed, tiny >> base >> small >> medium >> large
#     # model = load_model(name="tiny", device="cuda")
#     # model = load_model("small", device="cuda")
#     model = load_model("medium.en", device="cuda")
#
#     # Get the logger
#     logger = logging.getLogger(__name__)
#
#     # Ensure directory for completed transcriptions exists
#     os.makedirs(completed_transcription_directory, exist_ok=True)
#
#     try:
#         # for file_path in audio_files:
#         for file_path in glob.glob(os.path.join(completed_recordings_directory, "*.mp3")):
#             normalized_file_path = os.path.normpath(path=file_path)
#             logger.info(f"Transcribing {normalized_file_path}")
#             transcription = transcribe_audio_file(model, file_path)
#
#             # Create a new file for the transcription
#             filename = f"transcription_{os.path.basename(file_path)}"
#             transcription_filename = filename.replace("mp3", "txt")
#             completed_transcription_path = os.path.join(completed_transcription_directory, transcription_filename)
#             norm_comp_trans_path = os.path.normpath(path=completed_transcription_path)
#             with open(completed_transcription_path, 'w', encoding='utf-8') as f:
#                 f.write(f"{transcription}\n")
#             logger.info(f"Transcription saved to {norm_comp_trans_path}.")
#
#             # move audio file to archive directory
#             archive_recording_directory = "recordings/archive"
#             shutil.move(file_path, archive_recording_directory)
#             logger.info(f"{filename} moved to {archive_recording_directory}")
#     except Exception as e:
#         logger.error(f"An unexpected error occurred while transcribing and moving file(s): {type(e).__name__}, {e}")

def transcribe_and_move_audio_files(
        completed_recordings_directory: str = "recordings\\completed",
        archive_recordings_directory: str = "recordings\\archive",
        completed_transcription_directory: str = "transcriptions\\completed",
        max_retries: int = 3,
        min_unique_words: int = 100
) -> None:
    # Set up logging
    logger = logging.getLogger(__name__)

    # Ensure directory for completed transcriptions exists
    os.makedirs(completed_transcription_directory, exist_ok=True)
    # Ensure directory for completed recordings exists
    os.makedirs(completed_recordings_directory, exist_ok=True)

    client = Groq()

    for abbrevFileName in os.listdir(completed_recordings_directory):
        full_path = os.path.join(completed_recordings_directory, abbrevFileName)
        logger.info(f"Processing file: {abbrevFileName}")
        for i in range(max_retries):
            i += 1
            # Transcribe the audio file
            start_time = time.time()
            with open(file=full_path, mode='rb') as file:
                transcription = client.audio.transcriptions.create(
                    file=(full_path, file.read()),
                    model="whisper-large-v3",
                    prompt="",
                    response_format="json",
                    temperature=0
                )
            end_time = time.time()
            transcription_time = end_time - start_time
            logger.info(f"Attempt #{i}, Transcription of {abbrevFileName} completed in {transcription_time: .2f} seconds.")
            # print(f"Transcription of {abbrevFileName} completed in {transcription_time: .2f} seconds.")
            # print(f"transcription: \n{transcription}")

            # check transcription for errors
            num_words = len(set(transcription.text))
            if num_words > min_unique_words:
                # valid transcription
                logger.info(f"Attempt #{i}, number of unique words in transcription is {num_words}, continuing with this transcription")
                break
            # log retry attempts
            logger.info(f"Transcription text: \n{transcription.text}")
            if i < 3:
                logger.info(f"Attempt number {i} had {num_words} unique words. That seems too low, attempting a retry.")
            else:
                logger.info(f"On final attempt transcription had {num_words} unique words and will be used.")

        # Prepare the transcription filename and path
        transcription_filename = f"transcription_{abbrevFileName}".replace(".mp3", ".txt")
        transcription_path = os.path.join(completed_transcription_directory, transcription_filename)

        # Save the transcription
        with open(file=transcription_path, mode="w", encoding="utf-8") as f:
            f.write(transcription.text)

        logger.info(f"Transcription saved to {transcription_path}")
        # Move the original audio file to the archive directory
        shutil.move(full_path, archive_recordings_directory)
        logger.info(f"{abbrevFileName} moved to {archive_recordings_directory}")


def get_contents(completed_transcription_dir: str = "transcriptions/completed", archive_transcription_dir: str = "transcriptions/archive") -> str:
    """
    Walks a directory path and reads each text file concatenating their transcription, afterwards it moves the text file to an archive directory.
    :param completed_transcription_dir: Directory containing the transcription text files.
    :return: String containing all the transcriptions.
    """
    # Get the logger
    logger = logging.getLogger(__name__)

    # check for archive directory
    if not os.path.exists(archive_transcription_dir):
        os.makedirs(archive_transcription_dir)

    transcription = ""
    try:
        for root, dirs, files in os.walk(completed_transcription_dir):
            for file in files:
                if file.endswith(".txt"):
                    # full file path
                    file_path = os.path.join(root, file)
                    # normalize file path(s)
                    norm_file_path = os.path.normpath(path=file_path)
                    norm_archive_dir = os.path.normpath(path=archive_transcription_dir)
                    transcription += read_file(file_path=file_path)
                    shutil.move(src=file_path, dst=archive_transcription_dir)
                    logger.info(f"Moved {norm_file_path} to {norm_archive_dir}")
        return transcription
    except Exception as e:
        logger.error(f"An unexpected error occurred while getting transcription file contents: {type(e).__name__}, {e}")


def read_file(file_path: str) -> str:
    """
    Reads and returns the content of a given text file.

    Args:
        file_path (str): The path to the text file.

    Returns:
        str: The content of the file.

    Raises:
        FileNotFoundError: If the file does not exist at the given path.
        ValueError: If the file_path is not a string or is empty.
    """
    # Get the logger
    logger = logging.getLogger(__name__)

    norm_file_path = os.path.normpath(path=file_path)
    # Type checking for file_path
    if not isinstance(file_path, str) or not file_path:
        raise ValueError("The file path must be a non-empty string.")

    # Check if the file exists to avoid FileNotFoundError
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file at {file_path} does not exist.")

    # Reading the file
    with open(file=file_path, mode='r', encoding='utf-8') as f:
        content = f.read()  # Extracting content from the file
        logger.info(f"Completed reading file: {norm_file_path}.")
    return content


def save_response(model_response: str, save_dir: str = "responses") -> None:
    """
    Saves a model response to a text file in a specified directory.

    This function takes a string response from a model and saves it to a text file.
    The file is named with the current date and time to ensure uniqueness and is
    stored in the specified directory. The directory is created if it doesn't exist.

    Parameters:
    - model_response (str): The response text from the model to be saved.
    - save_dir (str): The directory where the response file will be saved. Default is "responses".

    Returns:
    None
    """
    # Get the logger instance
    logger = logging.getLogger(__name__)

    try:
        # Generate a unique filename using the current date and time
        file_name = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # Construct the full path for the file
        full_path = os.path.join(save_dir, file_name)

        # Ensure the save directory exists; create it if it does not
        os.makedirs(save_dir, exist_ok=True)

        # Open the file in write mode with UTF-8 encoding and save the model response
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(model_response)

        # Log the success message with the full path of the saved file
        norm_file_path = os.path.normpath(full_path)
        logger.info(f"Response saved to: {norm_file_path}.")
    except Exception as e:
        # Log any unexpected errors that occur during the save process
        logger.error(f"An unexpected error occurred while saving model response: {type(e).__name__}, {e}")


if __name__ == "__main__":
    completed_recordings_directory = "D:\\coding\\radioApps\\radioApp7\\recordings\\completed"
    archive_recordings_directory = "D:\\coding\\radioApps\\radioApp7\\recordings\\archive"
    completed_transcription_directory = "D:\\coding\\radioApps\\radioApp7\\transcriptions\\completed"
    transcribe_and_move_audio_files(completed_recordings_directory=completed_recordings_directory, archive_recordings_directory=archive_recordings_directory, completed_transcription_directory=completed_transcription_directory)
