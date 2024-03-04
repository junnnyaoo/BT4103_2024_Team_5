import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from pymongo import MongoClient
from bson.json_util import dumps

# Initializes your app with your bot token and socket mode handler
# If using local environ, replace with app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN")) 
api_key = os.getenv("OPENAI_API_KEY")

# Initialize MongoDB
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client.get_database("changestream")
collection = db.get_collection("collection")

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
    verbose=True, 
    memory=ConversationBufferMemory(memory_key="history", input_key="article")
)

def insert_category(collection_name,id,category):
        
    #Retrieve Collection
    collection = collection_name 
 
    #Focus on id
    filter = { '_id': id }
    print(filter)
 
    # Values to be updated / inserted 
    newvalues = { "$set": { 'category': category } }
    print(newvalues)

    collection.update_one(filter, newvalues) 
    
    print("UPDATED")



change_stream = mongo_client.changestream.collection.watch([{
    '$match': {
        'operationType': { '$in': ['insert'] }
    }
}])
#mongo_client.changestream.collection.insert_one({"_id": 12, "article": article_two})

for change in change_stream:
    print(dumps(change))

    #Get Current Document Field ID
    current_doc = change['fullDocument']['_id']

    #Retrieve Article/News Data
    article_insert = change['fullDocument']['news_data']
    
    #Let ChatGPT to Categorise
    output = chatgpt_chain.predict(article = article_insert) 

    #To make sure that there are no spacing which ChatGPT outputs " Category_Name" -> "Category_Name"
    output = output.strip()
    
    print(current_doc)
    print(output)

    #Insert Category to the Document
    insert_category(collection,current_doc,output)
    print('') # for readability only



    #Next Steps to do. Leave this running and do insertion on another py script. to see if it works. (after thursday meeting)
    #See if categorisation can be improved but am not too sure if this is for future sprints.