import logging

from openai import OpenAI


def run_openai(system_prompt: str, user_prompt: str) -> str:
    """
        Run the OpenAI model with the provided system and user prompts.

        Args:
            system_prompt (str): The system prompt for the OpenAI model.
            user_prompt (str): The user prompt for the OpenAI model.

        Returns:
            str: The generated response from the OpenAI model.
        """
    # Get the logger
    logger = logging.getLogger(__name__)

    # model = "gpt-4-turbo-preview"
    model = "gpt-4o"
    # model = "gpt-3.5-turbo"
    client = OpenAI()

    logger.info(msg=f"Sending request to {model}.")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        logger.info(msg="Model response received.")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"An unexpected error occurred getting models response: {type(e).__name__}, {e}")
