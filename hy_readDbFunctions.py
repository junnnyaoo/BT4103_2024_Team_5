#function to get latest news at the moment
def getLatestNews(collection, selected_categories):
    # News items for testing, afterwards will be calling read latest news data from db
    # tech_news_item_1 = (
    #     "1. *Headline*: Apple unveils new MacBook Pro with M2 chip and mini-LED display.\n"
    #     "   *Summary*: Apple introduces the latest MacBook Pro featuring its custom-designed M2 chip for enhanced performance and a stunning mini-LED display.\n"
    #     "   *Source*: The Verge\n"
    #     "   *Timestamp*: 21st February 2024, 9:00 AM\n"
    #     "   [Read more](link_to_full_article)\n\n\n"
    # )

    # tech_news_item_2 = (
    #     "2. *Headline*: Meta announces plans for metaverse integration across its platforms.\n"
    #     "   *Summary*: Meta (formerly Facebook) reveals its strategy to integrate metaverse features into Facebook, Instagram, and WhatsApp, aiming for a more immersive social experience.\n"
    #     "   *Source*: TechCrunch\n"
    #     "   *Timestamp*: 20th February 2024, 2:15 PM\n"
    #     "   [Read more](link_to_full_article)\n\n\n"
    # )

    # tech_news_item_3 = (
    #     "3. *Headline*: Tesla unveils new AI-powered autopilot system for Full Self-Driving (FSD) beta.\n"
    #     "   *Summary*: Tesla introduces its latest AI-powered autopilot system, promising improved performance and safety for its Full Self-Driving (FSD) beta testers.\n"
    #     "   *Source*: CNBC\n"
    #     "   *Timestamp*: 19th February 2024, 11:30 AM\n"
    #     "   [Read more](link_to_full_article)\n\n\n"
    # )
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
        # latest_news += "Id = " + str(news["_id"]) + "\n"
        # latest_news += "Text = " + str(news['article']) +"\n"
        latest_news += "url = " + str(news['url']) +"\n"
        latest_news += "published_at = " + str(news["published_at"]) + "\n"
        if n == 5:
            break
        n += 1
    latest_news = latest_news[:-1]  

    # Concatenate news items
    # latest_news = tech_news_item_1 + tech_news_item_2 + tech_news_item_3
    return latest_news

#function to get latest news according to category
def getCategoryNews():
    return 