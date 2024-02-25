import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from pymongo import MongoClient

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
template = """ You are a bot that will either provide news recommendations, news summaries or answer questions related to the news asked by users.
    You are speaking to a professional so keep the answer informative and concise.

    If given an article URL or asked to summarise a URL, Use this following format with their answers: 

    Title: <Title Name>
    Website Link: <Link of Website>
    Date of Article: <Get the latest date of publication, regardless of update or publish>
    Names to note: <Names of Company and people mentioned within the article>
    Key Topic: <Key topic of this article>
    Sentiment: <conduct sentiment analysis and let them know the sentiment>
    Trends & Statistics: <Include any trends and statistics found, make it short and do not repeat it in summary>

    Summary: <The summarised version of the article >
        
    If asked for news recommendations based on certain keywords or topics, return the recommendations using the additional information provided in this format:
    The ordering of the article recommendation should be based on the order of your previous output and not the order given by the additional information.

    Title: <Title Name>
    Website Link: <Link of Website>
    Date of Article: <Get the latest date of publication, regardless of update or publish>

    If not, just answer the questions with the information you know.


        Additional Information: {add_info}

        History:{history}

        Human: {human_input}
        Assistant:"""

prompt = PromptTemplate(
    input_variables=["history", "human_input", "add_info"], 
    template=template
)

chatgpt_chain = LLMChain(
    llm = OpenAI(openai_api_key=api_key,model="gpt-3.5-turbo-instruct", temperature=0), 
    prompt=prompt, 
    verbose=True, 
    memory=ConversationBufferMemory(memory_key="history", input_key="human_input")
)





# I did not add the code where I embedded the article and ingested into MongoDB. I did it separately in a Jupyter Notebook file. That one not important. 
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1536) # model used to embed text

def vector_search(query, collection):
    query_embedding = embeddings.embed_query(query)
    pipeline = [
        {
            "$vectorSearch": { # $vectorSearch is the specific function name
                "index": "vector_index", # The search index I created on MongoDB
                "queryVector": query_embedding, # The embedded query from the user that is used for searching
                "path": "data", # The relevant field of the document that is used for searching (in this case the full text of the news article)
                "limit": 3, # How many results you want the vectorSearch to show
                "numCandidates": 10 # How many documents you want vectorSearch to consider when searching
            }
        }
    ]
    
    results = collection.aggregate(pipeline) # executing the search
    return list(results) # compile results into a list

#Message handler for Slack
@app.message(".*")
def message_handler(message, say, logger):
    print(message)
    
    get_knowledge = vector_search(message['text'], collection) # Get the output from MongoDB after vector searching

    search_result = ''
    for result in get_knowledge:
        search_result += f"Title: {result.get('title', 'N/A')}, Link: {result.get('link', 'N/A')}"

    output = chatgpt_chain.predict(human_input = message['text'], add_info = search_result)   
    say(output)



# Start your app
if __name__ == "__main__":
    #if local environ, replace w/ : SocketModeHandler(app,os.environ.get("SLACK_BOT_TOKEN")).start()
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()