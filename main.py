import os
from dotenv import load_dotenv
from bot import Bot
from reddit_memes import MemeGenerator, reddit
from subscription_manager import SubscriptionManager
from quotes_generator import QuoteGenerator


load_dotenv()


if __name__ == "__main__":
    meme_generator = MemeGenerator(reddit)
    subscription_manager = SubscriptionManager()
    quote_generator = QuoteGenerator()
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    bot_cl = Bot(meme_generator, subscription_manager,
                 quote_generator, BOT_TOKEN).start()
