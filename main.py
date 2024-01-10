import os
from dotenv import load_dotenv
from bot import Bot
from reddit_memes import MemeGenerator, reddit


load_dotenv()


if __name__ == "__main__":
    meme_generator = MemeGenerator(reddit)
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    bot_cl = Bot(meme_generator, BOT_TOKEN).start()
