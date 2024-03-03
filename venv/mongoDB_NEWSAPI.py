import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings
from newsapi import NewsApiClient
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

newsapi = NewsApiClient(api_key= os.getenv("NEWS_API_KEY"))

##Adjust accordingly
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client.get_database("changestream")
collection = db.get_collection("collection")
##

try:
    mongo_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

top_headlines = newsapi.get_top_headlines(language='en',
                                          category= 'technology')



#Process the response
if top_headlines['status'] == 'ok':
    articles = top_headlines['articles']
    #for article in articles:
    for i in range(1,10):
        article = articles[i]

        title = article['title']
        url = article['url']
        published_at = article['publishedAt']
        
        # Check if the article is a YouTube video
        if url.startswith('https://www.youtube.com/watch?'):
            news_data = article['content']
        else:
            news_data = getFullContent(url)
        
        #Prevent Null Objects into new_data which will cause chatgpt to crash
        if news_data is None:
            news_data = ""

        # Insert data into MongoDB collection
        document = {
            "title": title,
            "url": url,
            "published_at": published_at,
            "news_data": news_data
        }
        collection.insert_one(document)
