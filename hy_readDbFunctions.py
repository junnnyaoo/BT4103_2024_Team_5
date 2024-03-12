from datetime import datetime
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
import string

#function to get latest news at the moment
def getNews(chatgpt_chain, collection, selected_categories, start_end_date = []):

    print(selected_categories)
    print(start_end_date)

    if 'All' in selected_categories:
        sorted_news = collection.find().sort("date", -1)
    else:
        # Query to filter news by categories
        query = {"newsCategory": {"$in": selected_categories}}

        # Sort the filtered news by published_at in descending order
        sorted_news = collection.find(query).sort("date", -1)

    #only top 5 news retrieved
    latest_news, n = "", 1

    if len(start_end_date) != 0:
        start = datetime.strptime(start_end_date[0], "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(start_end_date[1], "%Y-%m-%dT%H:%M:%S")

    for i, news in enumerate(sorted_news):
        
        # Define the format of the date string and parse it
        if len(start_end_date) != 0:
            news["date"] = news["date"].rsplit(' ', 1)[0]
            date_time = datetime.strptime(news["date"], "%Y-%m-%dT%H:%M:%S")

        if len(start_end_date) == 0 or start <= date_time <= end:
            data = ""
            latest_news += "*Article #" + str(n) + "*\n"

            #for testing and deployment
            data += "*Title*: " + str(news["title"])
            data += "*Website Link*: " + str(news['url'])
            data += "*Date of Article*: " + str(news["date"])
            
            #for deployment only

            # Filter out stop words and punctuation from the tokenized words, then join them back into a single string for gpt summarization
            words = nltk.word_tokenize(news["content"])
            stop_words = set(stopwords.words('english'))
            punctuation = set(string.punctuation)
            filtered_words = [word for word in words if word.lower() not in stop_words and word not in punctuation]
            filtered_text = ' '.join(filtered_words)

            data += "*information*: " + str(filtered_text)

            output = chatgpt_chain.predict(human_input = data, add_info="") 
            output = output.strip()
            latest_news += output + "\n\n"

            #comment this if the above is uncommented
            # latest_news += data + "\n\n"

            if n == 5:
                break
            n += 1
        else:
            continue
    latest_news = latest_news[:-2]  

    if len(latest_news) == 0:
        return "There are no news updates available currently."
    else:
        return latest_news
