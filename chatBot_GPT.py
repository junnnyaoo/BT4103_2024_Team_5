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
            text="News summarisation update here",
            post_at=schedule_timestamp
        )
        # Log the result
        logger.info(result)

    except SlackApiError as e:
        logger.error("Error scheduling message: {}".format(e))

#--------------------------------------------------------------------------------------------------------------------
#               Alex code
#--------------------------------------------------------------------------------------------------------------------

#Message handler for Slack
# @app.message(".*")
# def messaage_handler(message, say, logger):
#     print(message)
#     # output = chatgpt_chain.predict(human_input = message['text'])   
#     say("not connected to chatgpt, testing only")

#--------------------------------------------------------------------------------------------------------------------
#               Interactive message for scheduler
#--------------------------------------------------------------------------------------------------------------------

news_scheduler_blocks = [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "Please choose how frequently you'd like to receive news updates using the scheduler (News will be posted at 9am)."
			}
		},
		{
			"type": "actions",
			"elements": [
                {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Everyday"
					},
					"style": "primary",
					"value": "click_me_123",
                    "action_id": "1d"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "7 Days"
					},
					"style": "primary",
					"value": "click_me_123",
                    "action_id": "7d"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "14 Days"
					},
					"style": "primary",
					"value": "click_me_123",
                    "action_id": "14d"
				}
			]
		}
	]

#for direct msg    
@app.message("start newsbot")
def start(message, say):
    # client.chat_postMessage(
    #         channel= hy_id,
    #         text = "Please choose how frequently you'd like to receive news updates using the scheduler (News will be posted at 9am).",
    #         blocks= news_scheduler_blocks,
    #         as_user =True
    # )
    print(message)
    if message['channel_type'] == 'channel':
        say(channel= message['channel'],
                text = "Please choose how frequently you'd like to receive news updates using the scheduler (News will be posted at 9am).",
                blocks= news_scheduler_blocks,
                as_user =True)
    else:
        say(channel= message['user'],
                text = "Please choose how frequently you'd like to receive news updates using the scheduler (News will be posted at 9am).",
                blocks= news_scheduler_blocks,
                as_user =True)


# listener will be called every time a block element with the action_id "Everyday" is triggered
@app.action("1d")
def update_message(ack, body, say):
    #acknowledge inform Slack that your app has received the request.
    ack()
    # Update the message to reflect the action
    say("Clicked Everyday")
    next_days = 0
    #for testing
    now = datetime.datetime.now()
    seconds = now.second
    minutes = now.minute
    seconds += 15
    print(body)
    while next_days != 91:
        #---------- for testing -----------------
        #code will show 15 second later
        #wont work if your time now is close to the next hour
        seconds += 2
        print(minutes)
        print(seconds)
        print(now.hour)
        if seconds > 59:
            minutes += 1
            seconds = seconds - 60
        if next_days == 5:
            break
        if body['channel']['name'] == 'directmessage':
            schedule_news(now.hour, minutes, seconds, 0, body['user']['id'])
        else:
            schedule_news(now.hour, minutes, seconds, 0, body['channel']['id'])

        #---------- for deployment -----------------
        # schedule_news(9, 0, 0, next_day, body['channel'])
        # if body['channel']['name'] == 'directmessage':
        #     schedule_news(9, 0, 0, next_day, body['user']['id'])
        # else:
        #     schedule_news(9, 0, 0, next_day, body['channel']['id'])
        next_days += 1

    #schedule the same news for other days everyday

# Start your app
if __name__ == "__main__":
    #if local environ, replace w/ : SocketModeHandler(app,os.environ.get("SLACK_BOT_TOKEN")).start()
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()