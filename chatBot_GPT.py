import os
from dotenv import load_dotenv
import prompt_template
from prompt_template import template_2
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import ConversationChain, ConversationSummaryBufferMemory
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import datetime
#import blocks from our blocks python file
import blocks
#db functions
import hy_readDbFunctions
import logging
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
db = mongo_client.get_database("changestream")
collection = db.get_collection("collection")


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
    embeddings = article_embeddings.embed_query(content)
    article_json = {
        'title': title,
        'link': url,
        'data': embeddings,
        'article': content,
        # date how ah?        
    }

    collection.insert_one(article_json)
   
    output = {
        "Title": title,
        "Link": url,
        "Article": content
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
    seconds, minutes = now.second + 25, now.minute
    count, next_schedule, days_interval = 0, 0, int(days_interval)

    # max no. of schedule slack api allows is 120days
    while next_schedule < 120:
        #-------------------FOR TESTING---------------------------
        #code will show 15 second later
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
    tomorrow = datetime.date.today() + datetime.timedelta(days = next_schedule)
    scheduled_time = datetime.time(now.hour, minutes, seconds + 5)
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
        say(hy_readDbFunctions.getLatestNewsCategorized(chatgpt_chain2, collection, cleaned_selected_categories))
    
    elif message['channel_type'] != 'channel' and 'bot_id' not in message.keys():
        response = user_query(message['text'])

        say(response)

#--------------------------------------------------------------------------------------------------------------------
#               Slackbot startup
#--------------------------------------------------------------------------------------------------------------------
# Start your app
if __name__ == "__main__":
    #if local environ, replace w/ : SocketModeHandler(app,os.environ.get("SLACK_BOT_TOKEN")).start()
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()