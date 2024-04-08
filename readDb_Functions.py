from datetime import datetime
import nltk
from nltk.corpus import stopwords
import string
import os
from openai import OpenAI
api_key = os.getenv("OPENAI_API_KEY")

system_message = {"role": "system", 
                  "content": """
                    You are given an article(s) to summarize. Please respond with the following using information given. 
                    You are speaking to a professional so keep the answer informative and concise.
                    output the 4 items in this format, 
                    Add one asterisk infront and behind the word "Title","Website Link","Date of Article" and "Summary"
                        Title: (title here, do not add or change anything)
                        Website Link: (link here, do not add or change anything)
                        Date of Article: (date of publication here, do not add or change anything)
                        Summary: <Give an insightful summary of the article in six to eight lines. Include names to note, sentiment analysis, trends & statistics and key topic if available>
                    
                        Assistant:"""}

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def article_query(query):
    conversation = []
    conversation.append(system_message)
    conversation.append({"role": "user", "content": query})
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        temperature=0,
        messages= conversation
    )
    return response.choices[0].message.content.strip()

#function to get latest news at the moment
#Query to filter news by categories if categoreies is not 'All'
#Sort the filtered news by published_at in descending order
#only top 5 news retrieved
def getNews(collection, selected_categories, start_end_date = [], useGPT = True):

    print(selected_categories)
    print(start_end_date)

    output, count = "", 0

    if 'All' in selected_categories:
        sorted_news = collection.find().sort("date", -1)
    else:
        query = {"newsCategory": {"$in": selected_categories}}
        sorted_news = collection.find(query).sort("date", -1)

    #if date period is selected (not empty), convert to date time
    if len(start_end_date) != 0:
        start = datetime.strptime(start_end_date[0], "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(start_end_date[1], "%Y-%m-%dT%H:%M:%S")

    for i, news in enumerate(sorted_news):
        #only output 5 news
        if count == 3:
            break

        # set the format of the date string and parse it if user selected a specific date period
        if len(start_end_date) != 0:
            if 'Unknown publish date' != news["date"]:
                news["date"] = news["date"].rsplit(' ', 1)[0]
                date_time = datetime.strptime(news["date"], "%Y-%m-%dT%H:%M:%S")
            else:
                continue

        if len(start_end_date) == 0 or ('Unknown publish date' != news["date"] and start <= date_time <= end):

            output += "Article #" + str(count + 1) + "\n"
            data = ""
            data += "Title: " + str(news["title"])
            data += "URL: " + str(news['url'])
            data += "Date: " + str(news["date"])
            
            # Filter out stop words and punctuation from the tokenized words, then join them back into a single string for gpt summarization
            words = nltk.word_tokenize(news["content"])
            stop_words = set(stopwords.words('english'))
            punctuation = set(string.punctuation)
            filtered_words = [word for word in words if word.lower() not in stop_words and word not in punctuation]
            filtered_text = ' '.join(filtered_words)

            data += "Content: " + str(filtered_text)
            if useGPT:
                output += article_query(data) + "\n\n"
            else:
                output += data + "\n\n"

            count += 1

        else:
            continue
        
    if len(output) == 0:
        return "There are no news updates available currently."
    
    return output[:-2]  

