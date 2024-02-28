import os
import prompt_template
from prompt_template import template_2
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from pymongo import MongoClient

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
app = App(token=os.getenv("SLACK_BOT_TOKEN"), ignoring_self_events_enabled = False) 
api_key = os.getenv("OPENAI_API_KEY")
template_2 = template_2

# Initialize MongoDB
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client.get_database("news_articles")
collection = db.get_collection("cloud_technology")


#Langchain implementation
template = """ You are speaking to a professional who does not have much time, do an informative summary in 7 sentences maximum and keep the answer concise.
    If you do not know the title or link or date, just state TBC
    Go through the information and make a summary of the information in this following format with their answers: 

    Title: <Title Name>
    Website Link: <Link of Website>
    Date of Article: <Get the latest date of publication, regardless of update or publish>
    Names to note: <Names of Company and people mentioned within the article>
    Key Topic: <Key topic of this article>
    Sentiment: <conduct sentiment analysis and let them know the sentiment>
    Trends & Statistics: <Include any trends and statistics found, make it short and do not repeat it in summary>

    Summary: <The summarised version of the article>
    
    {history}
    Human: {human_input}
    Assistant:"""

prompt = PromptTemplate(
    input_variables=["history", "human_input"], 
    template=template
)

chatgpt_chain = LLMChain(
    llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0), 
    prompt=prompt, 
    verbose=True, 
    memory=ConversationBufferMemory(k=2),
)

#--------------------------------------------------------------------------------------------------------------------
#               SCHEDULE MESSAGE Slack API 
#--------------------------------------------------------------------------------------------------------------------
# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
logger = logging.getLogger(__name__)

def schedule_news(hour, minute, second, next_days, id):
    #Create a schedule using datetime library
    tomorrow = datetime.date.today() + datetime.timedelta(days = next_days)
    scheduled_time = datetime.time(hour, minute, second)
    schedule_timestamp = datetime.datetime.combine(tomorrow, scheduled_time).timestamp()
    try:
        # Call the chat.scheduleMessage method using the WebClient
        result = client.chat_scheduleMessage(
            channel=id,
            #here will be the relevent news update
            text= "Here are the latest news:",
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
#listener for scheduled msg "Here are the latest news:" so that the bot can fetch latest news on the scheduled day.
@app.message("Here are the latest news:")
def start(message, say):
    #need to check if this is bot, only bot can post news
    if 'bot_id' in message.keys():
        print("check")
        say(hy_readDbFunctions.getLatestNews(collection))

#listener for starting bot schedule
@app.message("start schedule")
@app.message("Your schedule has expired, please select a new schedule.")
def start(message, say):
    print(message)
    say(channel= message['channel'],
            text = "Please choose how frequently you'd like to receive news updates using the scheduler (News will be posted at 9am).",
            blocks= blocks.news_scheduler_blocks,
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
@app.action("category_select")
def update_message(ack, body, say):
    ack()
    # Extract selected options
    print(body)
    # Extracting all values of selected_options
    selected_options = []
    for value in body['state']['values'].values():
        if 'selected_options' in value.get('checkboxes-action', {}):
            selected_options.extend(option['value'] for option in value['checkboxes-action']['selected_options'])

    # Printing the extracted values
    print(selected_options)
    #code to retrieve from sql according to category
    say("category selection rececived: " + str(selected_options))

# action listener for news scheduling, whether if its 1d, 7d etc
@app.action("1d")
@app.action("7d")
@app.action("14d")
@app.action("30d")
def update_message(ack, body, say):
    #acknowledge inform Slack that your app has received the request.
    ack()

    #if user click this again it means he/she wants schedule to reset
    #get list of scheduled msgs
    scheduled_list = client.chat_scheduledMessages_list()['scheduled_messages']
    
    # print("\nBelow is list of scheduled bef delete")
    # print(client.chat_scheduledMessages_list())

    scheduled_msg_id_list = []
    for msg in scheduled_list:
        #append those that are in this channel
        if msg['channel_id'] == body['channel']['id']:
            scheduled_msg_id_list.append(msg['id'])

    # print("\nBelow is list of scheduled msg id list")
    # print(scheduled_msg_id_list)
    # delete those msgs scheduled in this channel
    for msg_id in scheduled_msg_id_list:
        client.chat_deleteScheduledMessage(channel=body['channel']['id'],scheduled_message_id=msg_id)

    # print("\nBelow is list of scheduled after delete")
    # print(client.chat_scheduledMessages_list())

    #for testing
    #25sec later post msg for testing
    now = datetime.datetime.now()
    seconds = now.second + 25
    minutes = now.minute
    print("\nBelow is body")
    print(body)

    count, next_schedule, days_interval = 0, 0, int(body['actions'][0]['value'])

    if len(scheduled_msg_id_list) == 0:
        say("We have received your schedule choices: News update every " + body['actions'][0]['value'] + " Days")
    else:
        say("We have rescheduled your schedule choices: News update every " + body['actions'][0]['value'] + " Days")

    # max no. of schedule slack api allows is 120days
    while next_schedule < 120:
        #---------- for testing -----------------
        #code will show 15 second later
        #wont work if your time now is close to the next hour
        if seconds >= 60:
            minutes += 1
            seconds = seconds - 60
        if count == 1:
            break
        if body['channel']['name'] == 'directmessage':
            schedule_news(now.hour, minutes, seconds, 0, body['user']['id'])
        else:
            schedule_news(now.hour, minutes, seconds, 0, body['channel']['id'])
        count += 1
    #     #---------- for deployment -----------------
    #     # schedule_news(9, 0, 0, next_schedule, body['channel'])
    #     # if body['channel']['name'] == 'directmessage':
    #     #     schedule_news(9, 0, 0, next_schedule, body['user']['id'])
    #     # else:
    #     #     schedule_news(9, 0, 0, next_schedule, body['channel']['id'])
    #     next_schedule += days_interval
        
    # print("\nBelow is list of scheduled after deleting all other schedules and scheduling new ones")
    # print(client.chat_scheduledMessages_list())  
        
    #need to change time to 9am
    tomorrow = datetime.date.today() + datetime.timedelta(days = next_schedule)
    scheduled_time = datetime.time(now.hour, minutes, seconds + 5)
    schedule_timestamp = datetime.datetime.combine(tomorrow, scheduled_time).timestamp()
    client.chat_scheduleMessage(
        channel=body['channel']['id'],
        #here will be the relevent news update
        text= "Your schedule has expired, please select a new schedule.",
        post_at=schedule_timestamp
    )


# all message handler for Slack
@app.message(".*")
def messaage_handler(message, say, logger):
    print(message)
    print("\n")
    if message['channel_type'] != 'channel' and 'bot_id' not in message.keys():
        # output = chatgpt_chain.predict(human_input = message['text'])   
        # say(output)
        say("not connected to chatgpt, testing only")

#--------------------------------------------------------------------------------------------------------------------
#               Slackbot startup
#--------------------------------------------------------------------------------------------------------------------
# Start your app
if __name__ == "__main__":
    #if local environ, replace w/ : SocketModeHandler(app,os.environ.get("SLACK_BOT_TOKEN")).start()
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()