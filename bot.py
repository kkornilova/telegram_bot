import os
from dotenv import load_dotenv
import telebot

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
