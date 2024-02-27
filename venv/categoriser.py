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
template = """ You are a bot that will be given an article and to categorise it. There are three categories, so only pick one. The three
    categories are 'Information Technology', 'Finance' or 'General'.

    If you do not know the category, just categorise as general.


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


article_one = '''As part of its efforts to tackle climate change, Singapore will be constructing the world’s largest facility to boost the ocean’s ability to absorb carbon dioxide (CO2) from the atmosphere. 
The US$20 million (S$27 million) plant, once fully operational in 2025, will be able to remove some 3,650 tonnes of CO2 from the ocean yearly, while helping PUB to decarbonise its water treatment processes, the national water agency said on Feb 27. 

When the seawater is pumped back into the ocean, it has the capacity to absorb more CO2 from the atmosphere.

The plan comes after two smaller pilot facilities – one in PUB’s R&D desalination plant in Tuas, and the other in the Port of Los Angeles – proved successful in removing CO2.

Both plants, which were set up in April 2023, are each able to remove some 100kg of the greenhouse gas from the ocean each day. 

The technology, designed by American start-up Equatic, works by pumping seawater from adjacent desalination plants through electricity. This leads to a series of chemical reactions that split the seawater into hydrogen and oxygen. The dissolved CO2 is combined with minerals in seawater like calcium and magnesium to produce solid limestone – essentially trapping the CO2 for at least 10,000 years. 

The process mimics the natural formation of seashells, and the solid calcium and magnesium-based materials can either be stored on the ocean floor, or potentially be used for construction materials if found viable.'''


article_two = '''The burgeoning artificial intelligence tools from companies such as OpenAI still have their share of skeptics, but don’t count JPMorgan Chase
 CEO Jamie Dimon among them.

The Wall Street titan told CNBC’s Leslie Picker on Monday that AI is not just a passing fad and is bigger than just the large language models such as Chat GPT. He compared the current moment favorably to the tech bubble around the start of the 21st century, when investor excitement seemingly got ahead of the actual changes.

“This is not hype. This is real. When we had the internet bubble the first time around … that was hype. This is not hype. It’s real,” Dimon said. “People are deploying it at different speeds, but it will handle a tremendous amount of stuff.”

JPMorgan has done work on the ability to use the new technologies internally, with Dimon saying that AI will eventually “be used in almost every job.” JPMorgan created a new role of chief data and analytics officer last year, in part to handle AI.

Dimon said Monday that there are 200 people at JPMorgan doing research on the large language models that have recently been rolled out by tech companies.

While acknowledging that AI can be used by bad actors, Dimon called himself a “big optimist” about the emerging technology, mentioning cybersecurity and pharmaceutical research as areas where it can be helpful.

“It may invent cancer cures because it can do things that the human mind simply cannot do,” Dimon said.'''




change_stream = mongo_client.changestream.collection.watch([{
    '$match': {
        'operationType': { '$in': ['insert'] }
    }
}])
mongo_client.changestream.collection.insert_one({"_id": 12, "article": article_two})

for change in change_stream:
    print(dumps(change))

    #Get Current Document Field ID
    current_doc = change['fullDocument']['_id']

    #Retrieve Article
    article_insert = change['fullDocument']['article']
    
    #Let ChatGPT to Categorise
    output = chatgpt_chain.predict(article = article_insert) 
    print(current_doc)
    print(output)

    #Insert Category to the Document
    insert_category(collection,current_doc,output)
    print('') # for readability only