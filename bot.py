import os
from dotenv import load_dotenv
import telebot
from telebot import types
import time
import re
from reddit_memes import get_reddit_meme

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

actions = "/get_meme - get meme\n/say_hello - get greetings regularly"

is_subscribed = False

time_unit_to_sec_map = {
    'sec': 1,
    "min": 60,
    "hour": 3600,
    "day": 86400,
}


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hi there!👋 How can I help you?\n"
                                      "/help - help\n" + actions)


@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(
        message.chat.id, f"😎 I can do many different things! Choose one of the commands below:\n{actions}")


@bot.message_handler(commands=["say_hello"])
def get_name(message):
    if is_subscribed:
        bot.send_message(
            message.chat.id, "Sorry, but you can get the greetings only once. Stop the previous command to start the new one.")
        return

    msg = bot.send_message(message.chat.id, "How can I call you?")
    bot.register_next_step_handler(msg, assign_name)


def assign_name(message):
    if message.text.startswith('/'):
        bot.process_new_messages([message])
        return

    name_regex = r'^[a-zA-Z\d]+$'

    if not re.match(name_regex, message.text):
        bot.reply_to(
            message, "Sorry, only latin alphabet and numbers are acceptable. Please try again or click /stop")
        bot.register_next_step_handler(message, assign_name)
        return

    name = message.text
    request_interval(message, name)


def request_interval(message, name):
    sent_msg = bot.send_message(
        message.chat.id, "Set the interval at which you want to receive the greetings.⏰\n\ni.e. 10 seconds, 2 minutes, 3 hours, 4 days\n\n*If you want to cancel the command - click /cancel")
    bot.register_next_step_handler(sent_msg, check_users_interval, name)


def check_users_interval(message, name):
    if message.text.startswith('/'):
        bot.process_new_messages([message])
        return

    number_regex = r'[\d]+'
    time_regex = r'\bsec|min|hour|day'

    match_number = re.findall(number_regex, message.text)
    match_string = re.findall(time_regex, message.text.lower())

    if not match_number or not match_string:
        bot.send_message(
            message.chat.id, "Please enter an interval as shown in the example!\n\ni.e. 10 seconds, 2 minutes, 3 hours, 4 days")
        bot.register_next_step_handler(message, check_users_interval, name)
        return

    number_unit = int(match_number[0])
    time_unit_key = match_string[0]

    interval_seconds = number_unit * time_unit_to_sec_map[time_unit_key]

    global is_subscribed
    is_subscribed = True

    say_hello(message, name, interval_seconds)


def say_hello(message, name, interval_seconds):
    if is_subscribed:
        bot.send_message(message.chat.id, f"Hello {
            name.title()}!❤️ \n\n*to stop sending - click:  /stop")
        time.sleep(interval_seconds)
        say_hello(message, name, interval_seconds)


@bot.message_handler(commands=["cancel"])
def cancel_command(message):
    global is_subscribed
    if is_subscribed:
        is_subscribed = False
        bot.reply_to(message, "The command was successfully canceled!")


@bot.message_handler(commands=["get_meme"])
def get_meme(message):
    bot.send_photo(message.chat.id, get_reddit_meme(), actions)


@bot.message_handler(commands=["stop"])
def stop(message):
    global is_subscribed
    is_subscribed = False
    bot.send_message(message.chat.id, "Sending is stopped😉\n" + actions)


@bot.message_handler(func=lambda msg: True)
def unknown_command(message):
    bot.send_message(
        message.chat.id, f"😶‍🌫️ Sorry, I don't understand your command: {message.text}.\nTry /help to see available commands.")


if __name__ == "__main__":
    bot.infinity_polling()
