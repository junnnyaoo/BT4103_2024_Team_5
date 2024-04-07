from pymongo import MongoClient
from newsapi import NewsApiClient
from newspaper import Article
from datetime import datetime, timedelta
import time
import threading
import pytz
from newspaper import Article, ArticleException
from requests.exceptions import HTTPError
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from nltk.tokenize import word_tokenize
from urllib.parse import urlparse
from dotenv import load_dotenv
import newsRev_BART
import newsRev_DeBERTa
import newsRev_BART
import newsRev_DeBERTa
import os
import feedparser

# Initial Setup
load_dotenv()
newsapi = NewsApiClient(os.getenv("NEWS_API_KEY"))
api_key = os.getenv("OPENAI_API_KEY")
mongo_client = MongoClient(os.getenv("MONGODB_URI"))

#--- Knowledge DB ----#
db = mongo_client.get_database("knowledge_db")
newsArticleCollection = db["tech_articles"]
###

#DB for testing 
#db = mongo_client.get_database("news_articles")
#newsArticleCollection = db.get_collection("newsArticleCollection")

# Getting Full Content from url from newsAPI
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


# Converting time from GMT (newsAPI default) to SGT timezone 
def getArticleDate(timestamp_utc):
    datetime_utc = datetime.strptime(timestamp_utc, "%Y-%m-%dT%H:%M:%SZ")
    # Convert to Singapore Time
    sgt_timezone = pytz.timezone("Asia/Singapore")
    datetime_sgt = datetime_utc.astimezone(sgt_timezone)
    # Format the datetime as a string
    timestamp_sgt = datetime_sgt.strftime("%Y-%m-%dT%H:%M:%S SGT")
    return timestamp_sgt

# News Categorisation with GPT
def categorizer_GPT(article_insert):
    try:
        #Defining Function + ChatGPT
        #Langchain implementation
        template = """ You are a bot that will be given an article and to categorise it. There are seven categories, so pick the best described one. The seven
        categories are 'AI', 'Quantum Computing', 'Green Computing', 'Robotics', 'Trust Technologies',
        'Anti-disinformation technologies', 'Communications Technologies'.
        
        AI includes Discriminative AI, Machine Learning, Generative AI

        Quantum Computing includes Quantum Internet, Quantum Communications, Quatum Computing

        Green Computing includes Green Serverless Computing, Green Edge Applications, Green Data Streaming

        Robotics

        Trust Technologies includes Privacy Enhancing Technologies, Regulation Technologies, Al Governance Technologies

        Anti-disinformation technologies includes Content Provenance Technologies, Anti-misinformation technologies, Detection of Generated Al content

        Communications Technologies includes 5G, Networks, Seamless

        However, if the article is not applicable to any category that you can categorise to your best ability, classify them as 'General'. However, this should be the last resort if
        the article does not fit into the categories at all.

        Make sure that there are no spacing before the first word.


        Human: {article}
        Assistant:"""

        prompt = PromptTemplate(
            input_variables=["article"], 
            template=template
        )

        chatgpt_chain = LLMChain(
            llm = OpenAI(openai_api_key=api_key,model="gpt-3.5-turbo-instruct", temperature=0), 
            prompt=prompt, 
            verbose=False,  # Set verbose to False to suppress output
            memory=ConversationBufferMemory(memory_key="history", input_key="article")
        )
        #Let ChatGPT to Categorise
        output = chatgpt_chain.predict(article=article_insert) 

        #To make sure that there are no spacing which ChatGPT outputs " Category_Name" -> "Category_Name"
        output = output.strip()

        return output

    except Exception as e:
        print(f"An error occurred: {e}")
        return "General"  # Return 'General' category in case of error
    
# News Relevance with GPT
def relevance_GPT(article_insert):
    #print('RELEVANCE GPT FUNCTION WORKING')
    try:
        #Defining Function + ChatGPT
        #Langchain implementation
        template = """ You are a bot that will be given an article and to deem if it is relevant to technology. 
        Please answer with Relevant or Irrelevant 

        Technology also includes the following:
        
        AI includes Discriminative AI, Machine Learning, Generative AI

        Quantum Computing includes Quantum Internet, Quantum Communications, Quatum Computing

        Green Computing includes Green Serverless Computing, Green Edge Applications, Green Data Streaming

        Robotics

        Trust Technologies includes Privacy Enhancing Technologies, Regulation Technologies, Al Governance Technologies

        Anti-disinformation technologies includes Content Provenance Technologies, Anti-misinformation technologies, Detection of Generated Al content

        Communications Technologies includes 5G, Networks, Seamless

        In terms of the article information, classify them as Relevant or Irrelevant. 

        Make sure that there are no spacing before the first word.


        Human: {article}
        Assistant:"""

        prompt = PromptTemplate(
            input_variables=["article"], 
            template=template
        )

        chatgpt_chain = LLMChain(
            llm = OpenAI(openai_api_key=api_key,model="gpt-3.5-turbo-instruct", temperature=0), 
            prompt=prompt, 
            verbose=False,  # Set verbose to False to suppress output
            memory=ConversationBufferMemory(memory_key="history", input_key="article")
        )
        #Let ChatGPT to Categorise
        output = chatgpt_chain.predict(article=article_insert) 

        #To make sure that there are no spacing which ChatGPT outputs " Category_Name" -> "Category_Name"
        output = output.strip()

        return output

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Irrelevant"  # Return 'Irrelevant'' category in case of error
# News Relevance with GPT
def relevance_GPT(article_insert):
    #print('RELEVANCE GPT FUNCTION WORKING')
    try:
        #Defining Function + ChatGPT
        #Langchain implementation
        template = """ You are a bot that will be given an article and to deem if it is relevant to technology. 
        Please answer with Relevant or Irrelevant 

        Technology also includes the following:
        
        AI includes Discriminative AI, Machine Learning, Generative AI

        Quantum Computing includes Quantum Internet, Quantum Communications, Quatum Computing

        Green Computing includes Green Serverless Computing, Green Edge Applications, Green Data Streaming

        Robotics

        Trust Technologies includes Privacy Enhancing Technologies, Regulation Technologies, Al Governance Technologies

        Anti-disinformation technologies includes Content Provenance Technologies, Anti-misinformation technologies, Detection of Generated Al content

        Communications Technologies includes 5G, Networks, Seamless

        In terms of the article information, classify them as Relevant or Irrelevant. 

        Make sure that there are no spacing before the first word.


        Human: {article}
        Assistant:"""

        prompt = PromptTemplate(
            input_variables=["article"], 
            template=template
        )

        chatgpt_chain = LLMChain(
            llm = OpenAI(openai_api_key=api_key,model="gpt-3.5-turbo-instruct", temperature=0), 
            prompt=prompt, 
            verbose=False,  # Set verbose to False to suppress output
            memory=ConversationBufferMemory(memory_key="history", input_key="article")
        )
        #Let ChatGPT to Categorise
        output = chatgpt_chain.predict(article=article_insert) 

        #To make sure that there are no spacing which ChatGPT outputs " Category_Name" -> "Category_Name"
        output = output.strip()

        return output

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Irrelevant"  # Return 'Irrelevant'' category in case of error


    # Getting Full Content from url from newsAPI
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


# News Relevance Filter
def newsRelevancy(article_content):
    countRelevance = 0
    
    gpt_Relevance = relevance_GPT(article_content)
    if (gpt_Relevance == "Relevant"):
        countRelevance += 1

    #print("GPT:")
    #print(gpt_Relevance)

    #LLM 1
    bart_Relevance = newsRev_BART.bart_Function(article_content)
    if (bart_Relevance == "Relevant"):
        countRelevance += 2
    #print("BART:")
    #print(bart_Relevance)
    #LLM 2
    deberta_relevance = newsRev_DeBERTa.DeBERTa_Function(article_content)
    if (deberta_relevance == "Relevant"):
        countRelevance += 3
    #print("deBerta:")
    #print(deberta_relevance)
        
    #False to deem article not relevant
    if countRelevance >= 3:
        print("Final: Relevant")
        return True
    else:
        print("Final: Irrelevant")
        return False



# News Relevance Filter
def newsRelevancy(article_content):
    countRelevance = 0
    
    gpt_Relevance = relevance_GPT(article_content)
    if (gpt_Relevance == "Relevant"):
        countRelevance += 1

    #print("GPT:")
    #print(gpt_Relevance)

    #LLM 1
    bart_Relevance = newsRev_BART.bart_Function(article_content)
    if (bart_Relevance == "Relevant"):
        countRelevance += 2
    #print("BART:")
    #print(bart_Relevance)
    #LLM 2
    deberta_relevance = newsRev_DeBERTa.DeBERTa_Function(article_content)
    if (deberta_relevance == "Relevant"):
        countRelevance += 3
    #print("deBerta:")
    #print(deberta_relevance)
        
    #False to deem article not relevant
    if countRelevance >= 3:
        print("Final: Relevant")
        return True
    else:
        print("Final: Irrelevant")
        return False


def check_duplicate(article_embedding, collection):

    pipeline = [
        {
            "$vectorSearch": { # $vectorSearch is the specific function name
                "index": "vector_index", # The search index I created on MongoDB
                "queryVector": article_embedding, # The embedded query from the user that is used for searching
                "path": "embeddedContent", # The relevant field of the document that is used for searching (in this case the full text of the news article)
                "limit": 15, # How many results you want the vectorSearch to show
                "numCandidates": 100 # How many documents you want vectorSearch to consider when searching
            }
        }, 
        {
                '$project': {
                '_id': 0, 
                'plot': 1, 
                'title': 1, 
                'score': {
                    '$meta': 'vectorSearchScore'
                }
            }
        }
    ]
    
    results = collection.aggregate(pipeline) # executing the search

    for i in results:    
        if i['score'] > 0.96: #prevent highly similar articles from being inserted into database
            return True  #True to being a duplicated article    
    
    return False



def articleScrapAndStore():

    tech_news = newsapi.get_everything(language='en',
                                        q = 'AI OR Quantum Computing OR Green Computing OR Robotics OR Trust Technologies OR Anti-disinformation technologies OR Communications Technologies',
                                        from_param="2024-04-01",
                                        to = '2024-04-07') #last scrapped 7th march 

    article_embeddings = OpenAIEmbeddings(api_key=api_key, model="text-embedding-3-large", dimensions=1536) # model used to embed article

    if tech_news['status'] == 'ok':
        articles = tech_news['articles']
        count = 0

        for article in articles:
            if count < 200:
                count += 1
            if count < 200:
                count += 1
                if article['url'].startswith('https://www.youtube.com/watch?'):
                    continue

                # Extract Source 
                source  = article['source']['name']

                # Extract author
                author = article['author']

                # Extract title
                title  = article['title']

                # Extract url
                url = article['url']

                # Scrap the full content from the URL
                content  = getFullContent(article['url'])

                #Filter out irrelevant article
                try:
                    if not newsRelevancy(content):
                        print("Rejected insertion to Database")
                        continue
                #catch articles that cannot be scrap
                except:
                    print('Error in content / Going to next article')
                    continue

                

                # News article content embedding 
                try:
                    embeddedContent  = article_embeddings.embed_query(content)
                except:
                    continue
                #prevent errors on sites that cannot be scrap

                
                

                # Block Duplicated News
                try:
                    if check_duplicate(embeddedContent,newsArticleCollection):
                        print("Duplicated News Detected. Rejected insertion.")
                        continue
                except:
                    print("Error with content - Under Duplicated News. Rejected insertion.")
                    continue


                # Article published date converted to SGT
                date = getArticleDate(article['publishedAt'])

                # News article sub-categorisation
                newsCategory = categorizer_GPT(content)

                article_data = {
                    'source': source, #Only taking out the name
                    'author': author,
                    'newsCategory': newsCategory,
                    'title': title,
                    'url': url,
                    'date': date,
                    'content': content,
                    'embeddedContent': embeddedContent
                }
                newsArticleCollection.insert_one(article_data)
                # collection.insert_one(article_data)
                #count += 1    
                #count += 1    
            else:
                break

def TX_RSS_ScrapAndStore():
    rss_feed_urls = [
        "https://techxplore.com/rss-feed/machine-learning-ai-news/",
        "https://techxplore.com/rss-feed/breaking/",
        "https://techxplore.com/rss-feed/energy-green-tech-news/",
        "https://techxplore.com/rss-feed/robotics-news/",
        "https://techxplore.com/rss-feed/telecom-news/",

    ]

    article_embeddings = OpenAIEmbeddings(api_key=api_key, model="text-embedding-3-large", dimensions=1536)

    for rss_feed_url in rss_feed_urls:
        feed = feedparser.parse(rss_feed_url)

        for entry in feed.entries:
            # if 'link' not in entry or 'title' not in entry or 'summary' not in entry:
            #     continue

            title = entry.title
            url = entry.link
            content  = getFullContent(url)

            # Filter out irrelevant articles
            try:
                if not newsRelevancy(content):
                    print("Rejected insertion to Database")
                    continue
            except Exception as e:
                print(f"Error in content / Going to next article: {str(e)}")
                continue

            # News article content embedding 
            try:
                embeddedContent = article_embeddings.embed_query(content)
            except Exception as e:
                print(f"Error embedding content: {str(e)}")
                continue

            # Block Duplicated News
            try:
                if check_duplicate(embeddedContent, newsArticleCollection):
                    print("Duplicated News Detected. Rejected insertion.")
                    continue
            except Exception as e:
                print(f"Error checking duplicate: {str(e)}")
                continue

            # Additional fields from the RSS feed
            article = Article(url)
            article.download()
            article.parse()
            
            author = ','.join(article.authors)  # Assuming TechXplore does not provide this info
            newsCategory = categorizer_GPT(content)

            # Article published date converted to SGT
            #date = entry.published  # Assuming TechXplore provides published date in the standard format
            date_format = "%a, %d %b %Y %H:%M:%S"
            parsed_date = datetime.strptime(entry.published[:-4], date_format) + timedelta(hours=4)

            # Since EDT is UTC-4, we adjust for that first before converting to SGT
            sgt = pytz.timezone('Asia/Singapore')  # Singapore Time Zone
            sgt_date = parsed_date.replace(tzinfo=pytz.utc).astimezone(sgt)

            # # Localize to EDT and then convert to SGT
            # localized_date = edt.localize(parsed_date)
            # converted_date = localized_date.astimezone(sgt)

            # Format the date in the desired format
            date = sgt_date.strftime("%Y-%m-%dT%H:%M:%S SGT")

            article_data = {
                'source': 'TechXplore',
                'author': author,
                'newsCategory': newsCategory,
                'title': title,
                'url': url,
                'date': date,
                'content': content,
                'embeddedContent': embeddedContent
            }
            newsArticleCollection.insert_one(article_data)


def add_toDB_check(source,author,title,url,date,content):
    article_embeddings = OpenAIEmbeddings(api_key=api_key, model="text-embedding-3-large", dimensions=1536) # model used to embed article
    to_Addchecker = True

    #Filter out irrelevant article
    try:
        if not newsRelevancy(content):
            print("Rejected insertion to Database")
            to_Addchecker = False
    #catch articles that cannot be scrap
    except:
        print('Error in content')
        to_Addchecker = False

    # News article content embedding 
    try:
        embeddedContent  = article_embeddings.embed_query(content)
    except:
        print("Article Content Cannot Be Embedded")
        to_Addchecker = False
    #prevent errors on sites that cannot be scrap

    # Block Duplicated News
    try:
        if check_duplicate(embeddedContent,newsArticleCollection):
            print("Duplicated News Detected. Rejected insertion.")
            to_Addchecker = False
            
    except:
        print("Error with content - Under Duplicated News. Rejected insertion.")
        to_Addchecker = False

    if to_Addchecker:
    # News article sub-categorisation
        newsCategory = categorizer_GPT(content)

        article_data = {
            'source': source, 
            'author': author,
            'newsCategory': newsCategory,
            'title': title,
            'url': url,
            'date': date,
            'content': content,
            'embeddedContent': embeddedContent
            }

        #To be adjusted to another function where we check if its relevant and store into MongoDB
        newsArticleCollection.insert_one(article_data)
        print("Added into Database")
        ###
    else:
        print("Not added into Database")


def add_toDB_check(source,author,title,url,date,content):
    article_embeddings = OpenAIEmbeddings(api_key=api_key, model="text-embedding-3-large", dimensions=1536) # model used to embed article
    to_Addchecker = True

    #Filter out irrelevant article
    try:
        if not newsRelevancy(content):
            print("Rejected insertion to Database")
            to_Addchecker = False
            
    #catch articles that cannot be scrap
    except:
        print('Error in content')
        to_Addchecker = False

    # News article content embedding
    if to_Addchecker:
        try:
            embeddedContent  = article_embeddings.embed_query(content)
        except:
            print("Article Content Cannot Be Embedded")
            to_Addchecker = False
        #prevent errors on sites that cannot be scrap

    

    # Block Duplicated News
    if to_Addchecker:
        try:
            if check_duplicate(embeddedContent,newsArticleCollection):
                print("Duplicated News Detected. Rejected insertion.")
                to_Addchecker = False
                
        except:
            print("Error with content - Under Duplicated News. Rejected insertion.")
            to_Addchecker = False

    if to_Addchecker:
    # News article sub-categorisation
        newsCategory = categorizer_GPT(content)

        article_data = {
            'source': source, 
            'author': author,
            'newsCategory': newsCategory,
            'title': title,
            'url': url,
            'date': date,
            'content': content,
            'embeddedContent': embeddedContent
            }

        #To be adjusted to another function where we check if its relevant and store into MongoDB
        newsArticleCollection.insert_one(article_data)
        print("Added into Database")
        ###
    else:
        print("Not added into Database")


def truncate_string_by_tokens(input_string):
    # Tokenize the input string
    tokens = word_tokenize(input_string)

    # Check if the number of tokens exceeds the specified limit
    if len(tokens) > 3800:
        # Truncate the string by joining the first max_tokens tokens
        truncated_string = ' '.join(tokens[:3800])
        return truncated_string
    else:
        # Return the original string if it doesn't exceed the limit
        return input_string


def urlScrapeAndStore(url):

    article = Article(url)
    article.download()
    article.parse()

    # Extract source
    parsed_url = urlparse(url)
    source  = parsed_url.netloc
    
    # Extract author
    try:
        author = article.authors[0]
    except:
        author= "Not Found"
    try:
        author = article.authors[0]
    except:
        author= "Not Found"

    # Extract title
    title  = article.title
    
    # Scrap the full content from the URL
    content  = article.text
    
    truncated_content = truncate_string_by_tokens(content)


    # Article published date converted to SGT
    if article.publish_date:
        date = article.publish_date.strftime("%Y-%m-%dT%H:%M:%S SGT")
    else:
        date = 'Unknown publish date'

    
    t1 = threading.Thread(target=add_toDB_check,args=(source,author,title,url,date,truncated_content))
    print('Thread Start')
    t1.start()
    


    output = {
        "Title": title,
        "Link": url,
        "Date": date,
        "Article": truncated_content
    }

    return output

#articleScrapAndStore()
#TX_RSS_ScrapAndStore()