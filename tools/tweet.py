import tweepy
from dotenv import load_dotenv
import os


def post_tweet(message):
    """Function to post a tweet
    Args: 
        message: String that is needed to be tweeted. It has no message cap (you will need a premium X account)
    Returns: -
    """
    
    # Load the environment variables from .env file
    load_dotenv()

    # Retrieve the X API keys and access tokens from environment variables
    bearer_token = os.getenv("X_BEARER_TOKEN")
    consumer_key = os.getenv("X_CONSUMER_KEY")
    consumer_secret = os.getenv("X_CONSUMER_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    # Authenticate with the X API
    client = tweepy.Client(bearer_token=bearer_token,
                        access_token=access_token,
                        access_token_secret=access_token_secret,
                        consumer_key=consumer_key,
                        consumer_secret=consumer_secret)

    # Send tweet
    response = client.create_tweet(text=message)
    print(f"https://x.com/BoletinBot/status/{response.data['id']}")
    return(f"https://x.com/BoletinBot/status/{response.data['id']}")