import os
from dotenv import load_dotenv
import telebot
from telebot import types
import time
from random import choice

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

actions = "/get_meme - get meme\n/say_hello - get greetings regularly"
images_urls = [
    "https://i.pinimg.com/originals/9d/c7/ba/9dc7ba948089037e327aab81156fb417.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2_6gj9GWC-UWVZnDMduVOi7AGbGnjYRt7Bpx2xUxImUgtynzQoUa88khozVq_gzgSpt4&usqp=CAU",
    "https://www.boredpanda.com/blog/wp-content/uploads/2023/05/cats-memes-funny-pics-cover_800.jpg",
    "https://pic-bstarstatic.akamaized.net/ugc/bd8be67f70d406c740575f3caab908b8.jpeg",
    "https://i0.wp.com/winkgo.com/wp-content/uploads/2018/05/55-Funniest-Cat-Memes-Ever-46.jpg?resize=720%2C963&ssl=1",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGHjxE21s3EHeqnHBygeVeLXrgz1l0C7BqEw&usqp=CAU"]

sent_images = []

is_subscribed = None


def say_hello(message):
    if is_subscribed:
        name = message.text
        bot.send_message(message.chat.id, f"Hello {
            name}!❤️ \n*to stop sending - click:  /stop")
        time.sleep(20)
        say_hello(message)


def get_image(message):
    image = choice(images_urls)
    if len(images_urls) > len(sent_images):
        if image not in sent_images:
            bot.send_photo(message.chat.id, image, actions)
            sent_images.append(image)
        else:
            get_image(message)
    else:
        bot.send_message(
            message.chat.id, "You've got all memes for today!🥳 Go back tomorrow!")


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hi there!👋 How can I help you?\n"
                                      "/help - help\n" + actions)


@bot.message_handler(commands=["get_meme", "say_hello", "help", "stop"])
def message_reply(message):
    if message.text == "/get_meme":
        get_image(message)

    elif message.text == "/help":
        bot.send_message(
            message.chat.id, f"😎 I can do many different things! Choose one of the commands below:\n{actions}")

    elif message.text == "/say_hello":
        global is_subscribed
        msg = bot.send_message(
            message.chat.id, "Please provide your name as I can call you:")
        is_subscribed = True
        bot.register_next_step_handler(msg, say_hello)

    elif message.text == "/stop":
        is_subscribed = False
        bot.send_message(message.chat.id, "Sending is stopped😉\n" + actions)

    else:
        unknown_command(message)


@bot.message_handler(func=lambda msg: True)
def unknown_command(message):
    bot.send_message(
        message.chat.id, f"😶‍🌫️ Sorry, I don't understand your command: {message.text}.\nTry /help to see available commands.")


bot.infinity_polling()
