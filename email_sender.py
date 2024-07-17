import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

from dotenv import load_dotenv

load_dotenv()


def send_email(subject: str, body: str, to_emails: List[str], from_email: str, password: str) -> None:
    """
    Send an email to multiple recipients using Gmail's SMTP server.

    :param subject: The subject of the email
    :param body: The body of the email
    :param to_emails: A list of recipient email addresses
    :param from_email: The sender's email address (must be a Gmail address)
    :param password: The password for the sender's email account
    """
    logger = logging.getLogger(__name__)
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Set up the server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)

        # Send email to each recipient
        for to_email in to_emails:
            msg['To'] = to_email
            server.send_message(msg)

        server.quit()
        print("Emails sent successfully.")
        logger.info(f"Emails sent successfully.")
    except Exception as e:
        print(f"Failed to send emails: {e}")
        logger.info(f"Failed to send emails: {e}")


if __name__ == "__main__":
    # Example usage
    pword = os.getenv("GMAIL_PASSWORD")
    send_email(
        subject="Test Email",
        body="This is a test email sent from a Python script.",
        to_emails=["solagbenro1@gmail.com"],
        # to_emails=["example1@example.com", "example2@example.com", "example3@example.com"],
        from_email="solagbenro@comcast.net",
        password=pword
    )
