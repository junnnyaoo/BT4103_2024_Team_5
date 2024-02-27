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

article_one = '''As part of its efforts to tackle climate change, Singapore will be constructing the world’s largest facility to boost the ocean’s ability to absorb carbon dioxide (CO2) from the atmosphere. 
The US$20 million (S$27 million) plant, once fully operational in 2025, will be able to remove some 3,650 tonnes of CO2 from the ocean yearly, while helping PUB to decarbonise its water treatment processes, the national water agency said on Feb 27. 

When the seawater is pumped back into the ocean, it has the capacity to absorb more CO2 from the atmosphere.

The plan comes after two smaller pilot facilities – one in PUB’s R&D desalination plant in Tuas, and the other in the Port of Los Angeles – proved successful in removing CO2.

Both plants, which were set up in April 2023, are each able to remove some 100kg of the greenhouse gas from the ocean each day. 

The technology, designed by American start-up Equatic, works by pumping seawater from adjacent desalination plants through electricity. This leads to a series of chemical reactions that split the seawater into hydrogen and oxygen. The dissolved CO2 is combined with minerals in seawater like calcium and magnesium to produce solid limestone – essentially trapping the CO2 for at least 10,000 years. 

The process mimics the natural formation of seashells, and the solid calcium and magnesium-based materials can either be stored on the ocean floor, or potentially be used for construction materials if found viable.'''


mongo_client.changestream.collection.insert_one({"_id": 13, "article": article_one})

mongo_client.changestream.collection.insert_one({"_id": 14, "article": article_one})