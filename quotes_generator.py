import requests
import os
from dotenv import load_dotenv

load_dotenv()


class QuoteGenerator:

    params = {"genre": "motivational",
              "count": 1}

    def get_quote(self):
        response = requests.get(os.environ.get("URL"),
                                params=QuoteGenerator.params).json()

        quote = response["data"][0]["quoteText"]
        author = response["data"][0]["quoteAuthor"]

        return (quote, author)
