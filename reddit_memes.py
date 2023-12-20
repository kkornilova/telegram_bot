import praw
import os
from dotenv import load_dotenv
from random import choice

load_dotenv()

reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    user_agent=os.environ.get("REDDIT_USER_AGENT")
)

telegram_supported_extensions = ["jpg", "png"]
meme_urls = []


def get_telegram_supported_urls():
    subreddit = reddit.subreddit("memes")
    all_posts = subreddit.top(limit=20)
    meme_urls.extend([post.url for post in all_posts if post.url[-3:]
                      in telegram_supported_extensions])


def get_reddit_meme():
    if not meme_urls:
        get_telegram_supported_urls()

    return meme_urls.pop()
