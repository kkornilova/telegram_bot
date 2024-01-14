import os
import telebot
import threading
import time
import re

from reddit_memes import MemeGenerator, reddit
from subscription_manager import SubscriptionManager
from quotes_generator import QuoteGenerator


time_unit_to_sec_map = {
    'sec': 1,
    "min": 60,
    "hour": 3600,
    "day": 86400,
}


class Bot:
    meme_generator = MemeGenerator(reddit)
    subscription_manager = SubscriptionManager()
    quote_generator = QuoteGenerator()

    commands_map = {"/get_meme": "- get meme",
                    "/get_motivation": "- get motivational quotes regularly",
                    "/help": "- help"}

    sent_quotes_counter = {}

    def __init__(self, bot_token):
        self.bot = telebot.TeleBot(bot_token)
        self.init_commands()

    def start(self):
        self.bot.infinity_polling()

    def init_commands(self):
        self.bot.message_handler(
            commands=["start", "hello"])(self.send_welcome)
        self.bot.message_handler(commands=["help"])(self.help)
        self.bot.message_handler(
            commands=["get_motivation"])(self.get_user_name)
        self.bot.message_handler(
            commands=["cancel"])(self.cancel_command)
        self.bot.message_handler(
            commands=["get_meme"])(self.get_meme)
        self.bot.message_handler(
            commands=["stop"])(self.stop)
        self.bot.message_handler(
            commands=["count_motivation"])(self.count_received_quotes)
        self.bot.message_handler(
            commands=["get_list_of_subscribers"])(self.get_password)
        self.bot.message_handler(
            func=lambda msg: True)(self.unknown_command)

    def format_commands_map(self):
        formatted = ''
        for k, v in self.commands_map.items():
            formatted += k + v + "\n"
        return formatted

    def send_welcome(self, message):
        self.bot.send_message(message.chat.id, "Hi there!👋 How can I help you?\n"
                              + self.format_commands_map())

    def help(self, message):
        self.bot.send_message(
            message.chat.id, f"😎 I can do many different things! Choose one of the commands below:\n{self.format_commands_map()}")

    def get_user_name(self, message):
        user_id = message.from_user.id

        if self.subscription_manager.is_subscribed(user_id):
            self.bot.send_message(message.chat.id,
                                  "Sorry, but you can subscribe only once.\n\nStop subscription to start the new one - /stop")
            return

        msg = self.bot.send_message(message.chat.id, "How can I call you?")
        self.bot.register_next_step_handler(msg, self.check_user_name_validity)

    def command_listener(func):
        def wrapper(*args):
            self, message = args
            if message.text.startswith('/'):
                self.bot.process_new_messages([message])
            else:
                return func(self, message)
        return wrapper

    @command_listener
    def check_user_name_validity(self, message):
        name_regex = r'^[a-zA-Z\d]+$'

        if not re.match(name_regex, message.text):
            self.bot.reply_to(
                message, "Sorry, only latin alphabet and numbers are acceptable. Please try again or /stop")
            self.bot.register_next_step_handler(
                message, self.check_user_name_validity)
            return

        self.subscription_manager.add_user_to_pending(message)

        self.request_interval(message)

    def request_interval(self, message):
        interval_set_instruction = "How often do you want to receive a motivation?⏰\n\nSet an interval e.g. 10 seconds, 2 minutes, 3 hours, 4 days\n\n*If you want to cancel the command - /cancel"

        msg = self.bot.send_message(message.chat.id, interval_set_instruction)
        self.bot.register_next_step_handler(msg, self.handle_interval_input)

    def handle_interval_input(self, message):
        if message.text == "/cancel":
            self.subscription_manager.remove_user_from_pending(message)
            self.bot.process_new_messages([message])
            return

        if message.text.startswith('/'):
            self.bot.process_new_messages([message])
            return

        interval = self.parse_valid_interval(message.text)

        if not interval:
            self.bot.send_message(
                message.chat.id, "Please enter an interval as shown in the example!\n\ne.g. 10 seconds, 2 minutes, 3 hours, 4 days")
            self.bot.register_next_step_handler(
                message, self.handle_interval_input)
            return

        name = self.subscription_manager.remove_user_from_pending(message)

        self.subscription_manager.add_to_subscribed_users(message)

        thread = threading.Thread(target=self.get_motivation, args=(
            message, name, interval))
        thread.start()

    def parse_valid_interval(self, interval):
        number_regex = r'[\d]+'
        time_regex = r'\bsec|min|hour|day'

        match_number = re.findall(number_regex, interval)
        match_string = re.findall(time_regex, interval.lower())

        if not match_number or not match_string:
            return False

        number_unit = int(match_number[0])
        time_unit_key = match_string[0]

        interval_in_seconds = number_unit * time_unit_to_sec_map[time_unit_key]

        return interval_in_seconds

    def get_motivation(self, message, name, interval_seconds):
        user_id = message.from_user.id

        if not self.subscription_manager.is_subscribed(user_id):
            return

        quote, author = self.quote_generator.get_quote()

        self.bot.send_message(message.chat.id,
                              f"Hei, {name.title()}\n\n{quote} ©\n\n{author}\n\nto stop sending - /stop,\nto see the number of received motivation - /count_motivation")

        if user_id in self.sent_quotes_counter:
            self.sent_quotes_counter[user_id] += 1

        else:
            self.sent_quotes_counter[user_id] = 1

        time.sleep(interval_seconds)
        self.get_motivation(message, name, interval_seconds)

    def count_received_quotes(self, message):
        user_id = message.from_user.id

        if user_id not in self.sent_quotes_counter:
            self.bot.send_message(message.chat.id, "You are not subscribed.")
            return

        self.bot.send_message(message.chat.id,
                              f"You've got {self.sent_quotes_counter[user_id]} motivational boost(s).")

    def get_password(self, message):
        msg = self.bot.send_message(message.chat.id, "Enter password: ")
        self.bot.register_next_step_handler(msg, self.check_password)

    @command_listener
    def check_password(self, message):
        if message.text != os.environ.get("bot_password"):
            self.bot.send_message(message.chat.id,
                                  "Wrong password! Try again or /cancel")
            self.get_password(message)
            return

        self.show_list_of_subscribers(message)

    def show_list_of_subscribers(self, message):
        usernames = self.subscription_manager.get_all_subscribed_users().values()
        if not usernames:
            self.bot.send_message(
                message.chat.id, "No subscribers at that moment")
            return

        sub_list = ''
        for username in usernames:
            sub_list += username + "\n"
        self.bot.send_message(
            message.chat.id, "Subscribers: " + "\n\n" + sub_list)

    def cancel_command(self, message):
        user_id = message.from_user.id

        if self.subscription_manager.is_subscribed(user_id):
            self.subscription_manager.remove_from_subscribed(user_id)
            self.sent_quotes_counter.pop(user_id)

        self.bot.reply_to(
            message, "The command was successfully canceled!")

    def get_meme(self, message):
        self.bot.send_photo(
            message.chat.id, self.meme_generator.get_reddit_meme(), self.format_commands_map())

    def stop(self, message):
        user_id = message.from_user.id

        if not self.subscription_manager.is_subscribed(user_id):
            self.bot.send_message(
                message.chat.id, "You're not subscribed.")
            return

        self.subscription_manager.remove_from_subscribed(user_id)
        self.sent_quotes_counter.pop(user_id)

        self.bot.send_message(
            message.chat.id, "Sending is stopped😉\n" + self.format_commands_map())

    def unknown_command(self, message):
        self.bot.send_message(
            message.chat.id, f"😶‍🌫️ Sorry, I don't understand your command: {message.text}.\nTry /help to see available commands.")
