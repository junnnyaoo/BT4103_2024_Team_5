from pymongo import MongoClient
from newsapi import NewsApiClient
from newspaper import Article
from datetime import datetime
import pytz
from newspaper import Article, ArticleException
from requests.exceptions import HTTPError
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from pymongo import MongoClient
from urllib.parse import urlparse
from dotenv import load_dotenv
import newsRev_BART
import os

# Initial Setup
load_dotenv()
newsapi = NewsApiClient(os.getenv("NEWS_API_KEY"))
api_key = os.getenv("OPENAI_API_KEY")
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client.get_database("matt_news_articles")
# collection = db.get_collection("demo")
# collection = db.get_collection("cloud_technology")
newsArticleCollection = db["mattjack_test"]


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
    print('RELEVANCE GPT FUNCTION WORKING')
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

    print(gpt_Relevance)

    #LLM 1
    bart_Relevance = newsRev_BART.bart_Function(article_content)
    if (bart_Relevance == "Relevant"):
        countRelevance += 1

    print(bart_Relevance)
    #LLM 2
        
    #False to deem article not relevant
    if countRelevance < 0:
        return False
    else:
        return True


## Ignore
# test_article= 'What the researchers have to say about the AI worm\n\n“\n\nThe study demonstrates that attackers can insert such prompts into inputs that, when processed by GenAI models, prompt the model to replicate the input as output (replication) and engage in malicious activities (payload). Additionally, these inputs compel the agent to deliver them (propagate) to new agents by exploiting the connectivity within the GenAI ecosystem. We demonstrate the application of Morris II against GenAI-powered email assistants in two use cases (spamming and exfiltrating personal data), under two settings (black-box and white-box accesses), using two types of input data (text and images).”\n\nSpamming: Morris II generated and sent spam emails through the compromised email assistant.\n\nMorris II generated and sent spam emails through the compromised email assistant. Data Exfiltration: The worm extracted sensitive personal data from the infected system.\n\nComPromptMized: Unleashing Zero-click Worms that Target GenAI-Powered Applications\n\nWhat AI companies said about the worm\n\nA group of researchers have developed a prototype AI worm called Morris II . According to the research papers (spotted by Wired), this first-generation AI worm can steal data, spread malware and spam users through AI-powered email assistants . However, it\'s important to note that this research was conducted in a controlled environment and the worm has not been deployed in the real world.Yet, this development highlights the potential vulnerabilities in generative AI models and emphasises the need for strict security measures.The research team, comprising Ben Nassi of Cornell Tech, Stav Cohen of the Israel Institute of Technology, and Ron Bitton of Intuit, named the worm after the original Morris worm. This notorious computer worm unleashed in 1988. Unlike its predecessor, Morris II targets AI apps, specifically those using large language models (LLMs) like Gemini Pro , ChatGPT 4.0, and LLaVA, to generate text and images.The worm uses a technique called " adversarial self-replicating prompts ." These prompts, when fed into the LLM, trick the model into replicating them and initiating malicious actions. This includes:The researchers described:The researchers successfully demonstrated the worm\'s capabilities in two scenarios:The researchers said that AI worms like this can help cyber criminals to extract confidential information, including credit card details, social security numbers and more. They also uploaded a video on YouTube to explain how the worm works:In a statement, an OpenAI spokesperson said: “They appear to have found a way to exploit prompt-injection type vulnerabilities by relying on user input that hasn’t been checked or filtered.”The spokesperson said that the company is making its systems more resilient and added that developers should use methods that ensure they are not working with harmful input.Meanwhile, Google refused to comment about the research.'
# print(categorizer_GPT(test_article))

# tech_news = newsapi.get_everything(language='en', q = 'quantum computing', page_size=10)
# print(tech_news)

# article = Article('https://gizmodo.com/google-launch-competition-figure-out-quantum-computers-1851308439')
# article.download()
# article.parse()

# newsCategory = categorizer_GPT(article.text)
# print(newsCategory)



def articleScrapAndStore():
    # tech_top_headlines = newsapi.get_top_headlines(language='en',category= 'technology',)
    tech_news = newsapi.get_everything(language='en', q = 'AI OR Quantum Computing OR Green Computing OR Robotics OR Trust Technologies OR Anti-disinformation technologies OR Communications Technologies')
    article_embeddings = OpenAIEmbeddings(api_key=api_key, model="text-embedding-3-large", dimensions=1536) # model used to embed article

    if tech_news['status'] == 'ok':
        articles = tech_news['articles']
        count = 0

        for article in articles:
            if count < 1:
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
                if not newsRelevancy(content):
                    print("Rejected insertion to Database")
                    continue


                # News article content embedding 
                try:
                    embeddedContent  = article_embeddings.embed_query(content)
                except:
                    continue
                #prevent errors on sites that cannot be scrap


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
                count += 1    
            else:
                break



def urlScrapeAndStore(url):

    url = url[1:-1]
    article = Article(url)
    article.download()
    article.parse()

    # Extract source
    parsed_url = urlparse(url)
    source  = parsed_url.netloc
    
    # Extract author
    author = article.authors[0]

    # Extract title
    title  = article.title
    
    # Scrap the full content from the URL
    content  = article.text

    # News article content embedding 
    article_embeddings = OpenAIEmbeddings(api_key=api_key, model="text-embedding-3-large", dimensions=1536) # model used to embed article
    embeddedContent  = article_embeddings.embed_query(content)

    # Article published date converted to SGT
    date = article.publish_date.strftime("%Y-%m-%dT%H:%M:%S SGT")

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
    ###
   
    output = {
        "Title": title,
        "Link": url,
        "Article": content
    }

    return output

articleScrapAndStore()
# for document in newsArticleCollection.find():
#     print(document)

# urlScrapeAndStore("https://medium.com/@123carmartin321/the-quantum-leap-how-quantum-computing-is-solving-the-worlds-most-complex-problems-85ac8adb43d6")
