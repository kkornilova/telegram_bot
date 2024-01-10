import os

import telebot
import threading
import time
import re


time_unit_to_sec_map = {
    'sec': 1,
    "min": 60,
    "hour": 3600,
    "day": 86400,
}


class Bot:
    commands_map = {"/get_meme": "- get meme",
                    "/say_hello": "- get greetings regularly",
                    "/help": "- help"}

    sent_greetings_counter = {}
    subscribed_users = {}

    def __init__(self, meme_generator, bot_token):
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
            commands=["count_greetings"])(self.count_received_greetings)
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

    def get_name(self, message):
        user_id = message.from_user.id

        if user_id in self.subscribed_users:
            self.bot.send_message(message.chat.id,
                                  "Sorry, but you can get the greetings only once.\n\nStop the previous command to start the new one - /stop")
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

        user_id = message.from_user.id
        username = message.from_user.username

        self.subscribed_users[user_id] = username

        thread = threading.Thread(target=self.say_hello, args=(
            message, name, interval_seconds))
        thread.start()

    def say_hello(self, message, name, interval_seconds):
        user_id = message.from_user.id

        if user_id not in self.subscribed_users:
            return

        self.bot.send_message(message.chat.id,
                              f"Hello {name.title()}!❤️ \n\n to stop sending - click:  /stop,\n to see the number of received greetings - click: /count_greetings")

        if user_id in self.sent_greetings_counter:
            self.sent_greetings_counter[user_id] += 1

        else:
            self.sent_greetings_counter[user_id] = 1

        time.sleep(interval_seconds)
        self.say_hello(message, name, interval_seconds)

    def count_received_greetings(self, message):
        user_id = message.from_user.id

        if user_id not in self.sent_greetings_counter:
            self.bot.send_message(message.chat.id, "You are not subscribed.")
            return

        self.bot.send_message(message.chat.id,
                              f"You've got {self.sent_greetings_counter[user_id]} greeting(s).")

    def get_password(self, message):
        msg = self.bot.send_message(message.chat.id, "Enter password: ")
        self.bot.register_next_step_handler(msg, self.check_password)

    def check_password(self, message):
        if message.text.startswith('/'):
            self.bot.process_new_messages([message])
            return
        if message.text != os.environ.get("bot_password"):
            self.bot.send_message(message.chat.id,
                                  "Wrong password! Try again or click /cancel")
            self.get_password(message)
            return

        self.show_list_of_subscribers(message)

    def show_list_of_subscribers(self, message):

        if len(self.subscribed_users) == 0:
            self.bot.send_message(
                message.chat.id, "No subscribers at that moment")
            return

        sub_list = ''
        for username in self.subscribed_users.values():
            sub_list += username + "\n"
        self.bot.send_message(
            message.chat.id, "Subscribers: " + "\n\n" + sub_list)

    def cancel_command(self, message):
        user_id = message.from_user.id
        if user_id in self.subscribed_users:
            self.subscribed_users.pop(user_id)
        self.bot.reply_to(
            message, "The command was successfully canceled!")

    def get_meme(self, message):
        self.bot.send_photo(
            message.chat.id, self.meme_generator.get_reddit_meme(), self.format_commands_map())

    def stop(self, message):
        user_id = message.from_user.id

        if user_id not in self.subscribed_users:
            self.bot.send_message(
                message.chat.id, "You're not subscribed.")
            return

        self.subscribed_users.pop(user_id)

        self.bot.send_message(
            message.chat.id, "Sending is stopped😉\n" + self.format_commands_map())

    def unknown_command(self, message):
        self.bot.send_message(
            message.chat.id, f"😶‍🌫️ Sorry, I don't understand your command: {message.text}.\nTry /help to see available commands.")
