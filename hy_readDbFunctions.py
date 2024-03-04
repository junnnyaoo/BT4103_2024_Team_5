#function to get latest news at the moment
def getLatestNewsCategorized(chatgpt_chain, collection, selected_categories):
    if 'All' in selected_categories:
        sorted_news = collection.find().sort("published_at", -1)
    else:
        # Query to filter news by categories
        query = {"category": {"$in": selected_categories}}

        # Sort the filtered news by published_at in descending order
        sorted_news = collection.find(query).sort("published_at", -1)

    #only top 5 news retrieved
    latest_news, n = "", 1
    
    for i, news in enumerate(sorted_news):

        data = ""
        latest_news += "*Article #" + str(n) + "*\n"
        data += "*Title*: " + str(news["title"]) + "\n"
        data += "*Website Link*: " + str(news['url']) + "\n"
        data += "*Date of Article*: " + str(news["published_at"])  + "\n"

        #for deployment
        # data += "*information*: " + str(news["news_data"])  + "\n"
        # output = chatgpt_chain.predict(human_input = data)  
        # output = output.strip()
        # latest_news += output + "\n\n"

        latest_news += data + "\n\n"

        if n == 3:
            break
        n += 1
    latest_news = latest_news[:-2]  

    if len(latest_news) == 0:
        return "There are no news updates available currently."
    else:
        return latest_news
