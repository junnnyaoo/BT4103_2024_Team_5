import os
import prompt_template
from prompt_template import template_2
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

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


chatgpt_chain = LLMChain(
    llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0), 
    prompt=prompt, 
    verbose=True, 
    memory=ConversationBufferMemory(k=2),
)

#Message handler for Slack
@app.message(".*")
def message_handler(message, say, logger):
    print(message)
    
    output = chatgpt_chain.predict(human_input = message['text'])   
    say(output)



# Start your app
if __name__ == "__main__":
    #if local environ, replace w/ : SocketModeHandler(app,os.environ.get("SLACK_BOT_TOKEN")).start()
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()