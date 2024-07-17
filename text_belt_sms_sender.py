import json
from datetime import datetime
import logging
import os
from typing import List
from dotenv import load_dotenv

import requests

load_dotenv()


def send_sms(phone_numbers: List[str], message: str, save_request_response: bool = False) -> None:
    """
    Sends an SMS message to a list of phone numbers using the Textbelt API.

    Args:
        phone_numbers (List[str]): A list of phone numbers to send the SMS to.
        message (str): The message to be sent.
        save_request_response (bool): Whether to save the response as json.

    Returns:
        None

    Raises:
        Requests.RequestException: If there is an error during the HTTP request.
        Exception: For any unexpected errors that occur during the process.
    """
    # Get a logger instance for logging the status and errors
    logger = logging.getLogger(__name__)

    # Retrieve the Textbelt API key from environment variables
    key = os.getenv("TEXTBELT_API_KEY")

    # URL for the Textbelt API endpoint
    textbelt_url = 'https://textbelt.com/text'

    try:
        # Iterate through each phone number in the provided list
        for phone_number in phone_numbers:
            # Prepare the payload for the POST request
            payload = {
                'phone': phone_number,
                'message': message,
                'key': key
            }
            # Send a POST request to the Textbelt API
            response = requests.post(url=textbelt_url, data=payload)

            # Check if the response status code indicates success
            if response.status_code == 200:
                # Log the remaining quota from the API response
                # print(f"response.json(): {response.json()}")
                logger.info(f"Response received, quotaRemaining: {response.json()['quotaRemaining']}.")
                if save_request_response:
                    request_dir = "requests"
                    os.makedirs(name=request_dir, exist_ok=True)
                    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    full_path = os.path.join(request_dir, filename)
                    with open(file=full_path, mode='w', encoding='utf-8') as f:
                        f.write(json.dumps(obj=response.json(), indent=4))
                    logger.info("Response from request.post() has been saved.")
    except requests.RequestException as e:
        # Log an error if there's a request exception
        logger.error(f"Request error: {type(e).__name__}, {e}")
    except Exception as e:
        # Log any other unexpected errors that occur
        logger.error(f"An unexpected error occurred while sending SMS: {type(e).__name__}, {e}")


if __name__ == "__main__":
    phone_numbers = [os.getenv("PHONE_NUMBER_ONE")]
    message = "test message, track quotaRemaining."
    send_sms(phone_numbers=phone_numbers, message=message, save_request_response=True)
