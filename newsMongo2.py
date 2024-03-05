from pymongo import MongoClient
from newsapi import NewsApiClient
from newspaper import Article
from datetime import datetime
import pytz
from newspaper import Article, ArticleException
from requests.exceptions import HTTPError
from newsdataapi import NewsDataApiClient



# Initialize MongoDB
mongo_client = MongoClient("mongodb+srv://newu:new1@cluster0.y8brcfm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client.get_database("news_articles")
collection = db.get_collection("cloud_technology")
NewsDataIOapi = NewsDataApiClient(apikey="pub_39474eeb92b9867027ff9ab46b2d4da9cdf0d")
# print(collection)
# response = NewsDataIOapi.news_api()
# response = NewsDataIOapi.news_api(q='technology', language= 'en', full_content=True) 
# print(response)

def getFullContent(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except ArticleException as e:
        print("Failed to parse article:", e)
    except HTTPError as e:
        print("HTTP Error:", e)
    return None

def getArticleDate(timestamp_utc):
    datetime_utc = datetime.strptime(timestamp_utc, "%Y-%m-%dT%H:%M:%SZ")
    # Convert to Singapore Time
    sgt_timezone = pytz.timezone("Asia/Singapore")
    datetime_sgt = datetime_utc.astimezone(sgt_timezone)
    # Format the datetime as a string
    timestamp_sgt = datetime_sgt.strftime("%Y-%m-%dT%H:%M:%S SGT")
    return timestamp_sgt

#Init
newsapi = NewsApiClient(api_key='0f1e87fe95c44a81ad7e1f80054bc8c4')



tech_top_headlines = newsapi.get_top_headlines(language='en',
                                          category= 'technology',)
biz_top_headlines = newsapi.get_top_headlines(language='en',
                                          category= 'business',)

if tech_top_headlines['status'] == 'ok':
    articles = tech_top_headlines['articles']
    for article in articles:
        article_data = {
            'source': article['source'],
            'author': article['author'],
            'newsCategory': 'Technology',
            'description': article['description'],
            'title': article['title'],
            'url': article['url'],
            'date': getArticleDate(article['publishedAt']),
            'content': getFullContent(article['url'])   
        }
        collection.insert_one(article_data)

if biz_top_headlines['status'] == 'ok':
    articles = biz_top_headlines['articles']
    for article in articles:
        article_data = {
            'source': article['source'],
            'author': article['author'],
            'newsCategory': 'Business',
            'description': article['description'],
            'title': article['title'],
            'url': article['url'],
            'date': getArticleDate(article['publishedAt']),
            'content': getFullContent(article['url'])
        }
        collection.insert_one(article_data)


for document in collection.find():
    print(document)
