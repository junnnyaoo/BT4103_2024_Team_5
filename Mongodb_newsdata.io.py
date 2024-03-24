import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings
from newsdataapi import NewsDataApiClient
import requests
from bs4 import BeautifulSoup
from newspaper import Article

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

newsdataioapi = NewsDataApiClient(apikey= os.getenv("NEWSDATA.IO_API_KEY"))
mongo_client = MongoClient(os.getenv("MONGODB_URI"))

db = mongo_client.get_database('news_articles')

collection = db.get_collection('technology')

try:
    mongo_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

top_headlines = newsdataioapi.news_api(language='en', category='technology')

# # Process the response
if top_headlines['status'] == 'success':
    articles = top_headlines['results']
    for article in articles:
        title = article['title']
        url = article['link']
        pub_date = article['pubDate']
        
        # Check if the article is a YouTube video
        #if url.startswith('https://www.youtube.com/watch?'):
        news_data = article['content']
        # else:
        #     news_data = getFullContent(url)
        
        # Insert data into MongoDB collection
        document = {
            "title": title,
            "url": url,
            "published_at": pub_date,
            "news_data": news_data
        }
        mongo_client.news_articles.technology.insert_one(document)

# Process the response
if top_headlines['status'] == 'success':
    articles = top_headlines['results']
    for article in articles:
        title = article['title']
        url = article['link']
        published_at = article['pubDate']
        
        # Check if the article is a YouTube video
        if url.startswith('https://www.youtube.com/watch?'):
            news_data = article['content']
        else:
            news_data = getFullContent(url)
        
        # Insert data into MongoDB collection
        document = {
            "title": title,
            "url": url,
            "published_at": published_at,
            "news_data": news_data
        }
        mongo_client.db.collection.insert_one(document)
