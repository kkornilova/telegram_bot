import praw
import os
from dotenv import load_dotenv


load_dotenv()

reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    user_agent=os.environ.get("REDDIT_USER_AGENT")
)

telegram_supported_extensions = ["jpg", "png"]
meme_urls = []

parameters = {
}


def get_telegram_supported_urls():
    global parameters
    subreddit = reddit.subreddit("memes")
    all_posts = subreddit.top(time_filter="year", limit=5, params=parameters)

    parameters = all_posts.params

    meme_urls.extend([post.url for post in all_posts if post.url[-3:]
                      in telegram_supported_extensions])

    if not meme_urls:
        get_telegram_supported_urls()


def get_reddit_meme():
    if not meme_urls:
        get_telegram_supported_urls()
    return meme_urls.pop()
