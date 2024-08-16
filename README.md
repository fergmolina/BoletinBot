# BoletinBot :robot::argentina:	
:argentina:	Un bot que que resumirá todos los días el _Boletín Oficial de Argentina_

:us: A bot that will summarize the _Boletín Oficial of Argentina_ every day

BoletinBot is live at X/Twitter in [https://x.com/BoletinBot](https://x.com/BoletinBot) 

<img src="https://pbs.twimg.com/profile_images/1820882645040979968/wl5n5ZnR_400x400.jpg">

## :godmode: Functionality
At the moment, BoletinBot will perform the following tasks:
- Check every weekday (no holidays) if there is a new Boletín Oficial on the official site.
- Summarize the information in the report
- Create a tweet with the generated information
- Send a Telegram message informing about the tweet created or an error message if it failed
- Run every day at 12:10 AM

## :computer: How does BoletinBot work?
Two APIs to send messages and one to create the content are used for this bot:
- It will check if there is a new Boletín Oficial on [https://www.boletinoficial.gob.ar/](https://www.boletinoficial.gob.ar/) 
- Using the obtained Boletín, the OpenAI API is used to create the bot's result
- The X API is then used to tweet all the created content
- The Telegram API is used to send a message with the tweet or an error message if it fails

## :rocket: Can I create my own bot?
YES! It's too easy. To do that, you'll first need to clone the repo and then install the requirements.txt. Next, you'll need to change the environment constants in the .env file:

* X_BEARER_TOKEN = Bearer Token from X API
* X_CONSUMER_KEY = Consumer Key from X API
* X_CONSUMER_SECRET= Consumer Secret from X API
* X_ACCESS_TOKEN= Access Token from X API
* X_ACCESS_TOKEN_SECRET= Access Token Secret from X API
* OPENAI_API_KEY= OpenAI API Key
* TELEGRAM_TOKEN= Telegram API token
* TELEGRAM_CHAT_ID= Telegram chat Id used to send the message

Enjoy!
