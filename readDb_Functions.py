from datetime import datetime
import nltk
from nltk.corpus import stopwords
# nltk.download('stopwords')
import string
import os
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferMemory
api_key = os.getenv("OPENAI_API_KEY")

template_summarisation = """ You are a bot that will do news summaries.
    You are speaking to a professional so keep the answer informative and concise.

    You are given an article(s) to summarize. Please respond with the following using information given. For the summary, summarize it using EXACTLY THREE LINES ONLY. If you can't do it, don't output.
    Title: <Title Name>
    Website Link: <Link of Website>
    Date of Article: <Get the latest date of publication>
    Names to note: <Names of Company and people mentioned within the article>
    Key Topic: <Key topic of this article>
    Sentiment: <conduct sentiment analysis and let them know the sentiment>
    Trends & Statistics: <Include any trends and statistics found, make it short and do not repeat it in summary>
    Summary: <The summarised version of the article in EXACTLY 3 lines> Please summarize using EXACTLY THREE lines. No more no less and finish the sentence with full stop ".".

        Human: {human_input}
        Assistant:
"""
prompt = PromptTemplate(
    input_variables=["history", "human_input", "add_info"], 
    template=template_summarisation
)

#function to get latest news at the moment
def getNews(collection, selected_categories, start_end_date = []):

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
        
        # Define the format of the date string and parse it if user selected date period
        if len(start_end_date) != 0:
            news["date"] = news["date"].rsplit(' ', 1)[0]
            date_time = datetime.strptime(news["date"], "%Y-%m-%dT%H:%M:%S")

        #read from db if date period is not selected or date is within the range of user's selected date period
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

            chatgpt_chain = LLMChain(
                llm = OpenAI(openai_api_key=api_key,model="gpt-3.5-turbo-instruct", temperature=0), 
                prompt=prompt, 
                verbose=True
            )
            
            # data += "*information*: " + news["content"]
            output = chatgpt_chain.predict(human_input = data) 
            output = output.strip()
            latest_news += output + "\n\n"

            #comment this if the above is uncommented
            # latest_news += data + "\n\n"

            if n == 5:
                break
            n += 1
        else:
            continue
    #remove "\n\n" for the last news
    latest_news = latest_news[:-2]  

    if len(latest_news) == 0:
        return "There are no news updates available currently."
    else:
        return latest_news
