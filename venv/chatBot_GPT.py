import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from langchain_openai import OpenAIEmbeddings
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from newspaper import Article

# Initializes your app with your bot token and socket mode handler
# If using local environ, replace with app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN")) 
api_key = os.getenv("OPENAI_API_KEY")

# Initialize MongoDB
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client.get_database("news_articles")
collection = db.get_collection("cloud_technology")


#Langchain implementation
template1 = """ You are a bot that will either provide news recommendations, news summaries or answer questions related to the news asked by users.
    You are speaking to a professional so keep the answer informative and concise.
        
    If asked for news recommendations based on certain keywords or topics, return the recommendations using the additional information provided in this format:
    The ordering of the article recommendation should be based on the order of your previous output and not the order given by the additional information.

    Title: <Title Name>
    Website Link: <Link of Website>
    Date of Article: <Get the latest date of publication>

    If not, just answer the questions with the information you know.


        Additional Information: {add_info}

        History:{history}

        Human: {human_input}
        Assistant:"""

template2 = """ You are a bot that will either provide news recommendations, news summaries or answer questions related to the news asked by users.
    You are speaking to a professional so keep the answer informative and concise.

    You are given an article(s) to summarize. Please respond with the following using information given.
    Title: <Title Name>
    Website Link: <Link of Website>
    Date of Article: <Get the latest date of publication>
    Names to note: <Names of Company and people mentioned within the article>
    Key Topic: <Key topic of this article>
    Sentiment: <conduct sentiment analysis and let them know the sentiment>
    Trends & Statistics: <Include any trends and statistics found, make it short and do not repeat it in summary>
    Summary: <The summarised version of the article>

        Additional Information: {add_info}

        History: {history}

        Human: {human_input}
        Assistant:
"""
prompt1 = PromptTemplate(
    input_variables=["history", "human_input", "add_info"], 
    template=template1
)

prompt2 = PromptTemplate(
    input_variables=["history", "human_input", "add_info"], 
    template=template2
)

chatgpt_chain1 = LLMChain(
    llm = OpenAI(openai_api_key=api_key,model="gpt-3.5-turbo-instruct", temperature=0), 
    prompt=prompt1, 
    verbose=True, 
    memory=ConversationBufferMemory(memory_key="history", input_key="human_input")
)

chatgpt_chain2 = LLMChain(
    llm = OpenAI(openai_api_key=api_key,model="gpt-3.5-turbo-instruct", temperature=0), 
    prompt=prompt2, 
    verbose=True, 
    memory=ConversationBufferMemory(memory_key="history", input_key="human_input")
)


article_embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1536) # model used to embed article
query_embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536) # model used to embed user queries

def vector_search(query, collection):
    query_embedding = query_embeddings.embed_query(query)
    pipeline = [
        {
            "$vectorSearch": { # $vectorSearch is the specific function name
                "index": "vector_index", # The search index I created on MongoDB
                "queryVector": query_embedding, # The embedded query from the user that is used for searching
                "path": "data", # The relevant field of the document that is used for searching (in this case the full text of the news article)
                "limit": 5, # How many results you want the vectorSearch to show
                "numCandidates": 100 # How many documents you want vectorSearch to consider when searching
            }
        }
    ]
    
    results = collection.aggregate(pipeline) # executing the search
    return list(results) # compile results into a list


def scrape_and_store(url):
    url = url[1:-1]
    article = Article(url)
    article.download()
    article.parse()
    title = article.title
    content = article.text
    # source =
    # author = article.authors
    # date = article.publish_date
    embeddings = article_embeddings.embed_query(content)
    article_json = {
        # 'source': source,
        # 'author': author,
        # 'date': date,
        # 'news_category': category, ### matthew's code
        'title': title,
        'link': url,
        'data': embeddings,
        'article': content,     
    }

    # collection.insert_one(article_json)
   
    output = {
        'title': title,
        'link': url,
        'article': content
    }
    return output


def find_url(text):
    x = text.split()
    url = []
    for word in x:
        if word.startswith("<https:") or word.startswith("<http:") or word.startswith("<www."):
            url.append(word)
    return url

def user_query(query):
    url = find_url(query)
    print(url)
    
    if url: # if array not empty
        output = ''
        articles = []
        for x in url:
            try:
                article = scrape_and_store(x)
                articles.append(article)
                output = chatgpt_chain2.predict(human_input = query, add_info=articles)
            except:
                output = "There was a problem accessing one of the links. Please ensure that the link is working."
                break
        return output
    else:
        get_knowledge = vector_search(query, collection) # Get the output from MongoDB after vector searching

        search_result = ''
        for result in get_knowledge:
            search_result += f"Title: {result.get('title', 'N/A')}, Link: {result.get('link', 'N/A')}"
        output = chatgpt_chain1.predict(human_input = query, add_info = search_result)  
        return output

#Message handler for Slack
@app.message(".*")
def message_handler(message, say, logger):
    print(message)
    
    response = user_query(message['text'])

    say(response)



# Start your app
if __name__ == "__main__":
    #if local environ, replace w/ : SocketModeHandler(app,os.environ.get("SLACK_BOT_TOKEN")).start()
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()