import os
from dotenv import load_dotenv
import prompt_template
from prompt_template import template_2
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain_openai import OpenAIEmbeddings
from langchain.agents import Tool, initialize_agent
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import datetime
#import blocks from our blocks python file
import blocks
#db functions
import readDb_Functions
import logging
from newsMongo import urlScrapeAndStore
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

#--------------------------------------------------------------------------------------------------------------------
#               Slackbot init
#--------------------------------------------------------------------------------------------------------------------
# Initializes your app with your bot token and socket mode handler
# If using local environ, replace with app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
load_dotenv()
app = App(token=os.getenv("SLACK_BOT_TOKEN"), ignoring_self_events_enabled = False) 
api_key = os.getenv("OPENAI_API_KEY")
template_2 = template_2

# Initialize MongoDB
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client.get_database("news_articles")
collection = db.get_collection("newsArticleCollection")




article_embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1536) # model used to embed article
query_embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536) # model used to embed user queries


def vector_search(query):
    query_embedding = query_embeddings.embed_query(query)
    pipeline = [
        {
            "$vectorSearch": { # $vectorSearch is the specific function name
                "index": "vector_index", # The search index I created on MongoDB
                "queryVector": query_embedding, # The embedded query from the user that is used for searching
                "path": "embedding", # The relevant field of the document that is used for searching (in this case the full text of the news article)
                "limit": 3, # How many results you want the vectorSearch to show
                "numCandidates": 100 # How many documents you want vectorSearch to consider when searching
            }
        }
    ]
    results = db['newsArticleCollection'].aggregate(pipeline) # executing the search
    search_result = ''
    for result in list(results):
        search_result += f"Title: {result.get('title', 'N/A')}, URL: {result.get('url', 'N/A')}, Date: {result.get('date', 'N/A')}, Content: {result.get('content', 'N/A')}"
    return search_result

def url(query):

    if query.startswith("<https:") or query.startswith("<http:") or query.startswith("<www."):
        query=query[1:-1]
    
    output = ''
    articles = []
  
    try:
        article = urlScrapeAndStore(query)
        articles.append(article)
        output = articles
    except:
        output = "There was a problem accessing one of the links. Please ensure that the link is working."
    
    return output

llm = ChatOpenAI(api_key=api_key, model='gpt-4-0125-preview', temperature=0, verbose=True)
memory = ConversationBufferWindowMemory(memory_key='chat_history',k = 5, return_messages=True)

tools = [Tool(
    name = 'QnA',
    func = vector_search,
    description = """
        For any news related questions, use this tool and the information generated to answer.
        When user ask to retrieve news such as "give me news" or "recommend me news", output the observation output as this format:
 
            Title: <Title Name>
            Website Link: <Link of Website>
            Date of Article: <Get the latest date of publication>
            Summary: <Give an insightful summary of the article in six to eight lines.>
    """
),
Tool(
    name = 'URL',
    func = url,
    description = """
        Use this tool if user sends an URL in the query. Access the URL and give an insightful summary of the news article from the URL. 
        Use the information generated from the URL given to help you form your summary. The summary should be substantial with at least six to eight lines.
    """
)
]

agent = initialize_agent(
    agent = 'conversational-react-description',
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=2,
    early_stopping_method='generate', 
    memory=memory,
    # return_intermediate_steps=True
    # agent_kwargs={
    #     'prefix': template
    # }
)

agent.agent.llm_chain.prompt.template = """ 

The Langchain LLM-powered assistant is designed to proficiently handle diverse tasks, such as recommending news and 
addressing queries related to technology and its updates. It's trained to generate human-like responses, ensuring natural 
conversations and relevant insights. Continuously learning and advancing, this assistant comprehends vast amounts of text to
deliver accurate information and engage in meaningful discussions. With its evolving capabilities, it's adept at providing assistance 
across various domains, making it a valuable resource for obtaining insights and engaging in informative conversations. Whether you seek 
specific answers or wish to delve into a topic, the assistant is primed to assist effectively.


TOOLS:
------

Assistant has access to the following tools:

> QnA: 
        For all questions, ALWAYS use this tool and the information with LLM to generate answer.
    
> URL:
        Use this tool if user sends an URL in the query. Access the URL and give an insightful summary of the news article from the URL. 
        Use the information generated from the URL given to help you form your summary. The summary should be substantial with at least six to eight lines.

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, must be either QnA or Date period 
Action Input: the input to the action (do not change content of new input)
Observation: the result of the action

```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
AI: [your response here]

```

Output note:

        When human ask for news article, ALWAYS do this:
        Using the observation result, output the 4 items in this format:
            Title: <Title Name>
            Website Link: <Link of Website>
            Date of Article: <Get the latest date of publication>
            Summary: <Give an insightful summary of the article in six to eight lines.>
        
        Output 3 articles if user did not specify the number of articles to be shown
Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
"""

#--------------------------------------------------------------------------------------------------------------------
#               SCHEDULE MESSAGE Slack API 
#--------------------------------------------------------------------------------------------------------------------
# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
logger = logging.getLogger(__name__)

#handling the schedule of news up to 120 days and days interval as selected
def handle_schedule(channel_id, channel_name, days_interval, selected_options_string):

    #-------------------FOR TESTING---------------------------
    #25sec later post msg for testing
    now = datetime.datetime.now()
    seconds, minutes = now.second + 20, now.minute
    count, next_schedule, days_interval = 0, 0, int(days_interval)

    # max no. of schedule slack api allows is 120days
    while next_schedule < 120:
        #-------------------FOR TESTING---------------------------
        #code will show 25 second later
        #wont work if your time now is close to the next hour
        if seconds >= 60:
            minutes += 1
            seconds = seconds - 60
        if count == 1:
            break
        if channel_name == 'directmessage':
            schedule_news(now.hour, minutes, seconds, 0, channel_id, selected_options_string)
        else:
            schedule_news(now.hour, minutes, seconds, 0, channel_id, selected_options_string)
        count += 1
    
    #     #-------------------FOR DEPLOY---------------------------
    #     # schedule_news(9, 0, 0, next_schedule, body['channel'])
    #     # if body['channel']['name'] == 'directmessage':
    #     #     schedule_news(9, 0, 0, next_schedule, body['user']['id'], selected_options_string)
    #     # else:
    #     #     schedule_news(9, 0, 0, next_schedule, body['channel']['id'], selected_options_string)
    #     next_schedule += days_interval
        
    # print("\nBelow is list of scheduled after deleting all other schedules and scheduling new ones")
    # print(client.chat_scheduledMessages_list())  
        
    #need to change time to 9am for deployment
    #this is for scheduling a prompt to 
    #ask user to choose schedule again
    #due to 120 days limit
    #for testing, to show schedule message expiry
    if seconds + 15 >= 60:
        minutes += 1
        seconds = seconds - 60
    tomorrow = datetime.date.today() + datetime.timedelta(days = next_schedule)
    scheduled_time = datetime.time(now.hour, minutes, seconds + 15)
    schedule_timestamp = datetime.datetime.combine(tomorrow, scheduled_time).timestamp()
    client.chat_scheduleMessage(
        channel=channel_id,
        text= "Your schedule has expired, please select a new schedule.",
        post_at=schedule_timestamp
    )

#handle each schedule of news request to slack api
def schedule_news(hour, minute, second, next_days, id, selected_options_string):
    #Create a schedule using datetime library
    tomorrow = datetime.date.today() + datetime.timedelta(days = next_days)
    scheduled_time = datetime.time(hour, minute, second)
    schedule_timestamp = datetime.datetime.combine(tomorrow, scheduled_time).timestamp()
    try:
        # Call the chat.scheduleMessage method using the WebClient
        result = client.chat_scheduleMessage(
            channel=id,
            #here will be the relevent news update
            text= "Here are the latest news filtered by selected category: " + selected_options_string,
            post_at=schedule_timestamp
        )
        # Log the result
        # print("\nBelow is schedule msg result")
        # logger.info(result)
        # print(result)
    except SlackApiError as e:
        logger.error("Error scheduling message: {}".format(e))

#--------------------------------------------------------------------------------------------------------------------
#               Slackbot listener
#--------------------------------------------------------------------------------------------------------------------

#listener for starting bot schedule
@app.message("start schedule")
@app.message("Your schedule has expired, please select a new schedule.")
def start(message, say):
    print(message)
    say(channel= message['channel'],
            text = "Please choose how frequently you'd like to receive news updates using the scheduler (News will be posted at 9am).",
            blocks= blocks.news_sched_category_blocks,
            as_user =True)

#listener for starting bot to show news category choices
@app.message("start news")
def start(message, say):
    print(message)
    say(channel= message['channel'],
            text = "Please select the news category you want to see.",
            blocks= blocks.news_category_blocks,
            as_user =True)

# action listener for news category, when user click this, we will output news filtered by category
@app.action("schedule_category_select")
def update_message(ack, body, say):
    ack()
    # Extract selected options
    print(body)

    #Extracting schedule days
    days_interval = body["state"]["values"]["schedule_radiobuttons"]["radio_buttons-action"]["selected_option"]["value"]
    # Extracting all values of selected_options
    selected_options = []
    selected_options.extend(option["value"] for option in body['state']['values']["category_checkboxes"]['checkboxes-action']['selected_options'])
    selected_options_string = ", ".join(selected_options)

    #if user click this again it means he/she wants schedule to reset
    #get list of scheduled msgs
    scheduled_list = client.chat_scheduledMessages_list()['scheduled_messages']
    scheduled_msg_id_list = []
    for msg in scheduled_list:
        #append those that are in this channel
        if msg['channel_id'] == body['channel']['id']:
            scheduled_msg_id_list.append(msg['id'])

    # print("\nBelow is list of scheduled bef delete")
    # print(client.chat_scheduledMessages_list())
    # print("\nBelow is list of scheduled msg id list")
    # print(scheduled_msg_id_list)
        
    # delete those msgs scheduled in this channel
    for msg_id in scheduled_msg_id_list:
        client.chat_deleteScheduledMessage(channel=body['channel']['id'],scheduled_message_id=msg_id)

    # print("\nBelow is list of scheduled after delete")
    # print(client.chat_scheduledMessages_list())
    
    if len(scheduled_msg_id_list) == 0:
        text = "We have received your schedule choices: News update every " + str(days_interval) + " Days" + ", categories: " + selected_options_string
    else:
        text = "We have rescheduled your schedule choices: News update every " + str(days_interval) + " Days" + ", categories: " + selected_options_string
    
    client.chat_update(channel = body['channel']['id'],ts = body['message']['ts'], text = text)
    #schedule the messages
    handle_schedule(body['channel']['id'], body['channel']['name'], days_interval, selected_options_string)

# action listener for category news
@app.action("category_select")
def update_message(ack, body, say):
    ack()
    print(body)

    selected_options = []
    selected_options.extend(option["value"] for option in body['state']['values']["category_checkboxes"]['checkboxes-action']['selected_options'])
    selected_options_string = ", ".join(selected_options)

    client.chat_update(channel = body['channel']['id'],ts = body['message']['ts'], text = "Category selection received: " + selected_options_string)
    say("Here are the latest news filtered by selected category: " + selected_options_string)

# action listener for category news
@app.action("date_select")
def update_message(ack, body, say):
    ack()
    print(body)
    
    selected_options = []
    selected_options.extend(option["value"] for option in body['state']['values']["category_checkboxes"]['checkboxes-action']['selected_options'])
    selected_options_string = ", ".join(selected_options)
    client.chat_delete(channel = body['channel']['id'],ts = body['message']['ts'])


    say(channel= body['channel']['id'],
            text = "Category selection received: " + selected_options_string,
            blocks= blocks.news_date_block,
            as_user =True)
    
import re
# action listener for category news
@app.action("date_selected")
def update_message(ack, body, say):
    ack()
    print("\nHERE")
    print(body)
    print(body['message']['text'])
    split_string = body['message']['text'].split("Category selection received: ")[1]
    # Split the categories
    selected_categories = split_string.split(", ")
    cleaned_selected_categories = []
    for item in selected_categories:
        cleaned_selected_categories.append(item.replace("&amp;", "&"))
    start_date = body['state']['values']['Start']['datepicker-action']['selected_date']
    end_date = body['state']['values']['End']['datepicker-action']['selected_date']

    client.chat_update(channel = body['channel']['id'],ts = body['message']['ts'], text = "Here are the news from " + start_date + " to " + end_date + " filtered by selected category: " + ", ".join(cleaned_selected_categories))
    #note that start and end date needs to be provided the hh mm ss for comparison later on
    say(readDb_Functions.getNews(collection, cleaned_selected_categories, [start_date + "T00:00:00",end_date  + "T23:59:59"]))

# for all message handler for Slack
@app.message(".*")
def messaage_handler(message, say, logger):
    print(message)
    print("\n")
    
    #listener for scheduled msg "Here are the latest news:" 
    #to fetch latest news on the scheduled day. 
    #need to check if this is bot, only bot can post news
    if 'bot_id' in message.keys() and message['text'].startswith("Here are the latest news"):
        # Split the string after "selected category:"
        print(message['text'])
        split_string = message['text'].split("selected category: ")[1]
        # Split the categories
        selected_categories = split_string.split(", ")
        cleaned_selected_categories = []
        for item in selected_categories:
            cleaned_selected_categories.append(item.replace("&amp;", "&"))
        #read news from db
        say(readDb_Functions.getNews(collection, cleaned_selected_categories))
    
    elif message['channel_type'] != 'channel' and 'bot_id' not in message.keys():
        response = agent(message['text'])

        say(response["output"])

#--------------------------------------------------------------------------------------------------------------------
#               Slackbot startup
#--------------------------------------------------------------------------------------------------------------------
# Start your app
if __name__ == "__main__":
    #if local environ, replace w/ : SocketModeHandler(app,os.environ.get("SLACK_BOT_TOKEN")).start()
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()