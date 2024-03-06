from pymongo import MongoClient
from newsapi import NewsApiClient
from newspaper import Article
from datetime import datetime
import pytz
from newspaper import Article, ArticleException
from requests.exceptions import HTTPError
from newsdataapi import NewsDataApiClient
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from pymongo import MongoClient
import os


# Initial Setup
api_key = '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'
mongo_client = MongoClient("mongodb+srv://newu:new1@cluster0.y8brcfm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client.get_database("news_articles")
collection = db.get_collection("cloud_technology")
newsapi = NewsApiClient(api_key='0f1e87fe95c44a81ad7e1f80054bc8c4')

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
        template = """ You are a bot that will be given an article and to categorise it. There are seven categories, so only pick one. The seven
        categories are 'Cloud Computing & Infrastructure', 'Consumer Technology', 'Cyber Security & Privacy', 'Data Science & AI', 'Decentralised Computing',
        'Digital Transformation', 'IT & Network Infrastructure'.

        However, if the content is not applicable to any category that you can categorise to your best ability, classify them as 'General'.
        If you do not know the category, just categorise as general.

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



## Ignore
# test_article= 'What the researchers have to say about the AI worm\n\n“\n\nThe study demonstrates that attackers can insert such prompts into inputs that, when processed by GenAI models, prompt the model to replicate the input as output (replication) and engage in malicious activities (payload). Additionally, these inputs compel the agent to deliver them (propagate) to new agents by exploiting the connectivity within the GenAI ecosystem. We demonstrate the application of Morris II against GenAI-powered email assistants in two use cases (spamming and exfiltrating personal data), under two settings (black-box and white-box accesses), using two types of input data (text and images).”\n\nSpamming: Morris II generated and sent spam emails through the compromised email assistant.\n\nMorris II generated and sent spam emails through the compromised email assistant. Data Exfiltration: The worm extracted sensitive personal data from the infected system.\n\nComPromptMized: Unleashing Zero-click Worms that Target GenAI-Powered Applications\n\nWhat AI companies said about the worm\n\nA group of researchers have developed a prototype AI worm called Morris II . According to the research papers (spotted by Wired), this first-generation AI worm can steal data, spread malware and spam users through AI-powered email assistants . However, it\'s important to note that this research was conducted in a controlled environment and the worm has not been deployed in the real world.Yet, this development highlights the potential vulnerabilities in generative AI models and emphasises the need for strict security measures.The research team, comprising Ben Nassi of Cornell Tech, Stav Cohen of the Israel Institute of Technology, and Ron Bitton of Intuit, named the worm after the original Morris worm. This notorious computer worm unleashed in 1988. Unlike its predecessor, Morris II targets AI apps, specifically those using large language models (LLMs) like Gemini Pro , ChatGPT 4.0, and LLaVA, to generate text and images.The worm uses a technique called " adversarial self-replicating prompts ." These prompts, when fed into the LLM, trick the model into replicating them and initiating malicious actions. This includes:The researchers described:The researchers successfully demonstrated the worm\'s capabilities in two scenarios:The researchers said that AI worms like this can help cyber criminals to extract confidential information, including credit card details, social security numbers and more. They also uploaded a video on YouTube to explain how the worm works:In a statement, an OpenAI spokesperson said: “They appear to have found a way to exploit prompt-injection type vulnerabilities by relying on user input that hasn’t been checked or filtered.”The spokesperson said that the company is making its systems more resilient and added that developers should use methods that ensure they are not working with harmful input.Meanwhile, Google refused to comment about the research.'
# print(categorizer_GPT(test_article))


def articleScrapAndStore():
    tech_top_headlines = newsapi.get_top_headlines(language='en',category= 'technology',)

    if tech_top_headlines['status'] == 'ok':
        articles = tech_top_headlines['articles']
        for article in articles:
            if article['url'].startswith('https://www.youtube.com/watch?'):
                continue
            article_data = {
                'source': article['source']['name'], #Only taking out the name
                'author': article['author'],
                'newsCategory': categorizer_GPT(getFullContent(article['url'])),
                'description': article['description'],
                'title': article['title'],
                'url': article['url'],
                'date': getArticleDate(article['publishedAt']),
                'content': getFullContent(article['url'])   
            }
            collection.insert_one(article_data)
            

# for document in collection.find():
#     print(document)
articleScrapAndStore()