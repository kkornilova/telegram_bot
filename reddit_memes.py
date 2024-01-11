import os
from dotenv import load_dotenv
import praw

load_dotenv()

reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    user_agent=os.environ.get("REDDIT_USER_AGENT")
)


class MemeGenerator:
    telegram_supported_extensions = ["jpg", "png"]
    parameters = {}
    meme_urls = []

    def __init__(self, meme_api: praw.Reddit):
        self.meme_api = meme_api

    def get_telegram_supported_urls(self):
        subreddit = self.meme_api.subreddit("memes")
        all_posts = subreddit.top(
            time_filter="day", limit=5, params=self.parameters)

        self.parameters = all_posts.params

        self.meme_urls.extend([post.url for post in all_posts if post.url[-3:]
                               in MemeGenerator.telegram_supported_extensions])

        if not self.meme_urls:
            self.get_telegram_supported_urls()

    def get_reddit_meme(self):
        if not self.meme_urls:
            self.get_telegram_supported_urls()
        return self.meme_urls.pop()
