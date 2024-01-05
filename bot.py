import os
from dotenv import load_dotenv

import telebot

from reddit_memes import MemeGenerator, reddit

import time
import re

load_dotenv()


time_unit_to_sec_map = {
    'sec': 1,
    "min": 60,
    "hour": 3600,
    "day": 86400,
}


class Bot:
    actions = "/get_meme - get meme\n/say_hello - get greetings regularly"
    is_subscribed = False

    def __init__(self, meme_generator: MemeGenerator, bot_token):
        self.bot = telebot.TeleBot(bot_token)
        self.meme_generator = meme_generator
        self.init_commands()

    def start(self):
        self.bot.infinity_polling()

    def init_commands(self):
        self.bot.message_handler(
            commands=["start", "hello"])(self.send_welcome)
        self.bot.message_handler(commands=["help"])(self.help)
        self.bot.message_handler(
            commands=["say_hello"])(self.get_name)
        self.bot.message_handler(
            commands=["cancel"])(self.cancel_command)
        self.bot.message_handler(
            commands=["get_meme"])(self.get_meme)
        self.bot.message_handler(
            commands=["stop"])(self.stop)
        self.bot.message_handler(
            func=lambda msg: True)(self.unknown_command)

    def send_welcome(self, message):
        self.bot.send_message(message.chat.id, "Hi there!👋 How can I help you?\n"
                              "/help - help\n" + self.actions)

    def help(self, message):
        self.bot.send_message(
            message.chat.id, f"😎 I can do many different things! Choose one of the commands below:\n{self.actions}")

    def get_name(self, message):
        if self.is_subscribed:
            self.bot.send_message(
                message.chat.id, "Sorry, but you can get the greetings only once. Stop the previous command to start the new one.")
            return

        msg = self.bot.send_message(message.chat.id, "How can I call you?")
        self.bot.register_next_step_handler(msg, self.assign_name)

    def assign_name(self, message):
        if message.text.startswith('/'):
            self.bot.process_new_messages([message])
            return

        name_regex = r'^[a-zA-Z\d]+$'

        if not re.match(name_regex, message.text):
            self.bot.reply_to(
                message, "Sorry, only latin alphabet and numbers are acceptable. Please try again or click /stop")
            self.bot.register_next_step_handler(message, self.assign_name)
            return

        name = message.text
        self.request_interval(message, name)

    def request_interval(self, message, name):
        sent_msg = self.bot.send_message(
            message.chat.id, "Set the interval at which you want to receive the greetings.⏰\n\ni.e. 10 seconds, 2 minutes, 3 hours, 4 days\n\n*If you want to cancel the command - click /cancel")
        self.bot.register_next_step_handler(
            sent_msg, self.check_users_interval, name)

    def check_users_interval(self, message, name):
        if message.text.startswith('/'):
            self.bot.process_new_messages([message])
            return

        number_regex = r'[\d]+'
        time_regex = r'\bsec|min|hour|day'

        match_number = re.findall(number_regex, message.text)
        match_string = re.findall(time_regex, message.text.lower())

        if not match_number or not match_string:
            self.bot.send_message(
                message.chat.id, "Please enter an interval as shown in the example!\n\ni.e. 10 seconds, 2 minutes, 3 hours, 4 days")
            self.bot.register_next_step_handler(
                message, self.check_users_interval, name)
            return

        number_unit = int(match_number[0])
        time_unit_key = match_string[0]

        interval_seconds = number_unit * time_unit_to_sec_map[time_unit_key]

        self.is_subscribed = True

        self.say_hello(message, name, interval_seconds)

    def say_hello(self, message, name, interval_seconds):
        if self.is_subscribed:
            self.bot.send_message(message.chat.id, f"Hello {
                name.title()}!❤️ \n\n*to stop sending - click:  /stop")
            time.sleep(interval_seconds)
            self.say_hello(message, name, interval_seconds)

    def cancel_command(self, message):
        if self.is_subscribed:
            self.is_subscribed = False
            self.bot.reply_to(
                message, "The command was successfully canceled!")

    def get_meme(self, message):
        self.bot.send_photo(
            message.chat.id, self.meme_generator.get_reddit_meme(), self.actions)

    def stop(self, message):
        self.is_subscribed = False
        self.bot.send_message(
            message.chat.id, "Sending is stopped😉\n" + self.actions)

    def unknown_command(self, message):
        self.bot.send_message(
            message.chat.id, f"😶‍🌫️ Sorry, I don't understand your command: {message.text}.\nTry /help to see available commands.")


if __name__ == "__main__":
    meme_generator = MemeGenerator(reddit)
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    bot_cl = Bot(meme_generator, BOT_TOKEN).start()
