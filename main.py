import os
import logging
from dotenv import load_dotenv

from stream_capture import download_audio_chunk
from transcriptions import transcribe_and_move_audio_files, get_contents, save_response
from models import run_openai
from text_belt_sms_sender import send_sms

load_dotenv()

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("log.log", mode='a'),  # Log to file
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)


def main():
    # download audio stream (https://playerservices.streamtheworld.com/api/livestream-redirect/KQMVFM.mp3)
    # url = 'https://18743.live.streamtheworld.com/KQMVFM.mp3?dist=hubbard&source=hubbard-web&ttag=web&gdpr=0'
    # url = 'https://23093.live.streamtheworld.com/KQMVFM.mp3?dist=hubbard&source=hubbard-web&ttag=web&gdpr=0'
    url = 'https://18743.live.streamtheworld.com/KQMVFM.mp3'
    download_audio_chunk(url=url, duration=660)
    # transcribe file(s) to transcriptions directory
    transcribe_and_move_audio_files()
    # walk transcription directory and extract contents from file
    t_dir = "transcriptions/completed"
    text_transcript = get_contents(completed_transcription_dir=t_dir)
    system_prompt = f"""You are a contestant attempting to win Olivia Rodrigo concert tickets from a radio station named 'Movin 92.5'. In order to win you must determine, then extract the winning word within a large corpus of text."""

    user_prompt = f"""You are attempting to extract the winning/code word out of a large corpus of text to win Olivia Rodrigo
    concert tickets. The winning word may be referred to as the 'winning' word, the 'code' word, the
    'magic' word, the 'entry' word or something similar to those. If the winning word is determined, respond back with
    the winning word, and the context or sentence that led you to determine the word. If you cannot determine the 
    winning word, reply back saying so. The text is provided below.

    <text_transcript>
    {text_transcript}
    </text_transcript>"""

    # get model response
    response = run_openai(system_prompt=system_prompt, user_prompt=user_prompt)
    save_response(model_response=response, save_dir="responses")
    # phone numbers to send sms to
    phone_numbers = [os.getenv("PHONE_NUMBER_ONE"), os.getenv("PHONE_NUMBER_TWO"), os.getenv("PHONE_NUMBER_THREE")]
    # phone_numbers = [os.getenv("PHONE_NUMBER_ONE")]
    send_sms(phone_numbers=phone_numbers, message=response, save_request_response=True)
    logger.info(f"model response: {response}")
    print(f"model response: {response}")


if __name__ == "__main__":
    main()
