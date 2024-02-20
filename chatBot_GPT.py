import os
import prompt_template
from prompt_template import template_2
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

import datetime

import logging
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Initializes your app with your bot token and socket mode handler
# If using local environ, replace with app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
app = App(token=os.getenv("SLACK_BOT_TOKEN")) 
api_key = os.getenv("OPENAI_API_KEY")
template_2 = template_2

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

# chatgpt_chain = LLMChain(
#     llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0), 
#     prompt=prompt, 
#     verbose=True, 
#     memory=ConversationBufferMemory(k=2),
# )

#--------------------------------------------------------------------------------------------------------------------
#               SCHEDULE MESSAGE Slack API #Method 1 
#--------------------------------------------------------------------------------------------------------------------
# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
logger = logging.getLogger(__name__)

# News items
news_item_1 = (
    "*Latest News:*\n"
    "1. *Headline*: Biden announces new infrastructure plan to rebuild roads and bridges.\n"
    "   *Summary*: President Biden unveils a $2 trillion infrastructure proposal aimed at modernizing the nation's transportation infrastructure and tackling climate change.\n"
    "   *Source*: CNN\n"
    "   *Timestamp*: 21st February 2024, 10:30 AM\n"
    "   [Read more](link_to_full_article)\n\n"
)

news_item_2 = (
    "2. *Headline*: SpaceX successfully launches crewed mission to the International Space Station.\n"
    "   *Summary*: SpaceX Crew Dragon spacecraft carrying four astronauts docks with the ISS, marking another milestone in commercial spaceflight.\n"
    "   *Source*: Reuters\n"
    "   *Timestamp*: 20th February 2024, 3:45 PM\n"
    "   [Read more](link_to_full_article)\n\n"
)

news_item_3 = (
    "3. *Headline*: WHO warns of new variant spreading rapidly across Europe.\n"
    "   *Summary*: World Health Organization alerts countries to the spread of a highly transmissible new variant of COVID-19 across several European nations.\n"
    "   *Source*: BBC News\n"
    "   *Timestamp*: 19th February 2024, 8:00 PM\n"
    "   [Read more](link_to_full_article)\n\n"
)

# Concatenate news items
news_example = news_item_1 + news_item_2 + news_item_3

def schedule_news(hour, minute, second, next_days, id):
    
    #Create a schedule using datetime library
    tomorrow = datetime.date.today()  + datetime.timedelta(days = next_days)
    scheduled_time = datetime.time(hour, minute, second)
    schedule_timestamp = datetime.datetime.combine(tomorrow, scheduled_time).timestamp()
    try:
        # Call the chat.scheduleMessage method using the WebClient
        result = client.chat_scheduleMessage(
            channel=id,
            #here will be the relevent news update
            text= news_example,
            post_at=schedule_timestamp
        )
        # Log the result
        print("\nBelow is schedule msg result")
        logger.info(result)
        print(result)

    except SlackApiError as e:
        logger.error("Error scheduling message: {}".format(e))

#--------------------------------------------------------------------------------------------------------------------
#               Interactive message for scheduler
#--------------------------------------------------------------------------------------------------------------------

news_scheduler_blocks = [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "Please choose how frequently (every 1/7/14/30 days) you'd like to receive news updates (News will be posted at 9am)."
			}
		},
		{
			"type": "actions",
			"elements": [
                {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "1 Days"
					},
					"style": "primary",
					"value": "1 Days",
                    "action_id": "1d"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "7 Days"
					},
					"style": "primary",
					"value": "7 Days",
                    "action_id": "7d"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "14 Days"
					},
					"style": "primary",
					"value": "14 Days",
                    "action_id": "14d"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "30 Days"
					},
					"style": "primary",
					"value": "30 Days",
                    "action_id": "30d"
				}
			]
		}
	]

#for direct msg    
@app.message("start newsbot")
def start(message, say):
    print(message)
    say(channel= message['channel'],
            text = "Please choose how frequently you'd like to receive news updates using the scheduler (News will be posted at 9am).",
            blocks= news_scheduler_blocks,
            as_user =True)
    

# listener will be called every time a block element with these action_id is called
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
    
    print("\nBelow is list of scheduled bef delete")
    print(client.chat_scheduledMessages_list())

    scheduled_msg_id_list = []
    for msg in scheduled_list:
        #append those that are in this channel
        if msg['channel_id'] == body['channel']['id']:
            scheduled_msg_id_list.append(msg['id'])
    print("\nBelow is list of scheduled msg id list")
    print(scheduled_msg_id_list)
    # delete those msgs scheduled in this channel
    for msg_id in scheduled_msg_id_list:
        client.chat_deleteScheduledMessage(channel=body['channel']['id'],scheduled_message_id=msg_id)

    print("\nBelow is list of scheduled after delete")
    print(client.chat_scheduledMessages_list())

    #for testing
    now = datetime.datetime.now()
    seconds = now.second + 25
    minutes = now.minute
    print("\nBelow is body")
    print(body)
    count = 0

    next_schedule, days_interval = 0, 0
    if body['actions'][0]['value'] == '1 Days':
        days_interval = 1
    elif body['actions'][0]['value'] == '7 Days':
        days_interval = 7
    elif body['actions'][0]['value'] == '14 Days':
        days_interval = 14
    elif body['actions'][0]['value'] == '30 Days':
        days_interval = 30
    
    if len(scheduled_msg_id_list) == 0:
        say("We have received your schedule choices: News update every " + body['actions'][0]['value'])
    else:
        say("We have rescheduled your schedule choices: News update every " + body['actions'][0]['value'])

    # max no. of schedule slack api allows is 120days
    while next_schedule <= 30:

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
        
    print("\nBelow is list of scheduled after deleting all other schedules and scheduling new ones")
    print(client.chat_scheduledMessages_list())

#--------------------------------------------------------------------------------------------------------------------
#               Alex code
#--------------------------------------------------------------------------------------------------------------------

# Message handler for Slack
@app.message(".*")
def messaage_handler(message, say, logger):
    print(message)
    if message['channel_type'] != 'channel':
        # output = chatgpt_chain.predict(human_input = message['text'])   
        say("not connected to chatgpt, testing only")

# Start your app
if __name__ == "__main__":
    #if local environ, replace w/ : SocketModeHandler(app,os.environ.get("SLACK_BOT_TOKEN")).start()
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()