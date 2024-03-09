#function to get latest news at the moment
def getLatestNewsCategorized(chatgpt_chain, collection, selected_categories, start_end_date = []):
    print(start_end_date)
    if 'All' in selected_categories:
        
        if len(start_end_date) != 0:
            query = {
                "published_at": {
                    "$gte": start_end_date[0],
                    "$lte": start_end_date[1]
                }
            }
            # Sort the filtered news by published_at in descending order
            sorted_news = collection.find(query).sort("published_at", -1)
        else:
            sorted_news = collection.find().sort("published_at", -1)
    else:
        if len(start_end_date) != 0:
            query = {
                "category": {"$in": selected_categories},
                "published_at": {
                    "$gte": start_end_date[0],
                    "$lte": start_end_date[1]
                }
            }
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

        #for testing and deployment
        data += "*Title*: " + str(news["title"]) + "\n"
        data += "*Website Link*: " + str(news['url']) + "\n"
        data += "*Date of Article*: " + str(news["date"])  + "\n"
        
        #for deployment only
        # data += "*information*: " + str(news["content"])  + "\n"
        # output = chatgpt_chain.predict(human_input = data, add_info="") 
        # output = output.strip()
        # latest_news += output + "\n\n"

        latest_news += data + "\n\n"

        if n == 5:
            break
        n += 1
    latest_news = latest_news[:-2]  

    if len(latest_news) == 0:
        return "There are no news updates available currently."
    else:
        return latest_news
