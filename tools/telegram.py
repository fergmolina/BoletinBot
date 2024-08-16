import requests
from dotenv import load_dotenv
import os

def send_message_telegram(message, url, error=False):
    # Load the environment variables from .env file
    load_dotenv()

    # Retrieve the X API keys and access tokens from environment variables
    bot_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if error == False:
        text = f"{message}: {url}"
    else:
        text = f"Error: {message}"

    try:
        response = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", {
            'chat_id': chat_id,
            'text': text
        })

        print('Message sent:', response.json())
    except Exception as error:
        print('Failed to send message:', error)
