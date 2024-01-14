import os
from dotenv import load_dotenv
from bot import Bot


load_dotenv()


if __name__ == "__main__":
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    bot_cl = Bot(BOT_TOKEN).start()
