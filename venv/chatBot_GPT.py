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


####################################################### DID NOT USE THIS YET
#Langchain implementation
template = """Assistant is a large language model trained by OpenAI.

    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

    {history}
    Human: {human_input}
    Assistant:"""

prompt = PromptTemplate(
    input_variables=["history", "human_input"], 
    template=template
)

chatgpt_chain = LLMChain(
    llm = OpenAI(openai_api_key=api_key,model="gpt-3.5-turbo-instruct", temperature=0), 
    prompt=prompt, 
    verbose=True, 
    memory=ConversationBufferMemory(k=2),
)
####################################################### DID NOT USE THIS YET




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
                "limit": 1, # How many results you want the vectorSearch to show
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

    # output = chatgpt_chain.predict(human_input = message['text'])   
    say(search_result)



# Start your app
if __name__ == "__main__":
    #if local environ, replace w/ : SocketModeHandler(app,os.environ.get("SLACK_BOT_TOKEN")).start()
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()