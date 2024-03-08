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
        say(hy_readDbFunctions.getLatestNewsCategorized(chatgpt_chain, collection, cleaned_selected_categories))
    
    elif message['channel_type'] != 'channel' and 'bot_id' not in message.keys():
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