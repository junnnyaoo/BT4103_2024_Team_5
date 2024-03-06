import psycopg2
from newsapi import NewsApiClient
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import os
from dotenv import load_dotenv

load_dotenv()


def getFullContent(url):
    # Fetch the HTML content of the article using Requests
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Use Newspaper3k to extract the full article content
    article = Article(url)
    article.download()
    article.parse()

    # Get the full text content of the article
    full_text = article.text

    return full_text


# Init

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

newsapi = NewsApiClient(api_key= NEWS_API_KEY)

top_headlines = newsapi.get_top_headlines(language='en',
                                          category= 'technology',)

id = 1

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
conn = psycopg2.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

# Process the response
cursor = conn.cursor()


if top_headlines['status'] == 'ok':
    articles = top_headlines['articles']
    for article in articles:
        title = article['title']
        url = article['url']
        published_at = article['publishedAt']
        if url.startswith('https://www.youtube.com/watch?'):
            news_data = article['content']
        else:
            news_data = getFullContent(url)
        cursor.execute("INSERT INTO \"public\".\"NewsArticles\" (id, title, url, published_at, news_data) VALUES (%s, %s, %s, %s, %s)", (id, title, url, published_at, news_data))
        id = id +1


# Commit changes and close cursor and connection
conn.commit()
cursor.close()
conn.close()