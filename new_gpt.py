
import os
from openai import OpenAI

system_message = {"role": "system", 
                  "content": """You are a bot that will either provide news recommendations, news summaries or answer questions related to the news asked by users.
    You are speaking to a professional so keep the answer informative and concise.

    You are given an article(s) to summarize. Please respond with the following using information given.
    Title: <Title Name>
    Website Link: <Link of Website>
    Date of Article: <Get the latest date of publication>
    Names to note: <Names of Company and people mentioned within the article>
    Key Topic: <Key topic of this article>
    Sentiment: <conduct sentiment analysis and let them know the sentiment>
    Trends & Statistics: <Include any trends and statistics found, make it short and do not repeat it in summary>
    Summary: <The summarised version of the article>

        Assistant:"""}

conversation = []
conversation.append(system_message)

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.getenv("OPENAI_API_KEY"),
)

def user_query(query):
    #add user query to conversation for gpt's response 
    conversation.append({"role": "user", "content": query})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages= conversation
        # temperature=0.7,
    )
    #add bot reply to conversation
    conversation.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content.strip()

from newsMongo import urlScrapeAndStore
#link test
url = ['<https://www.cnbc.com/2023/04/30/cloud-providers-amazon-microsoft-and-google-face-spending-cuts.html>']
output = ''
articles = []
for x in url:
    article = urlScrapeAndStore(x)
    articles.append(article)
    output = user_query(str(articles))
    print("Here is output \n")
    print(output)
    print("\n")

# response = user_query("""Summarise this Coral Bay Nickel Corporation donated uniforms and medical kits to Palawan’s barangay health workers on Monday, an initiative enhancing local healthcare support.

# The Provincial Information Office said Vice Governor Leoncio Ola and Board Member Marivic Roxas, chairperson of the Committee on Health and Social Services of the Sangguniang Panlalawigan, received the donations.

# Ernesto Llacuna, community relations manager of CBNC, facilitated the distribution of approximately 2,000 barangya health workers (BHW) uniforms, 150 BP monitors, and 150 thermometers to health workers in the southern region of the province.

# Attendees included Board Members Juan Antonio Alvarez and Luzviminda Bautista, Dr. Justyn Barbosa, Medical Specialist IV, representing Provincial Health Officer Dr. Faye Erika Q. Labrador, and CVHW Manager Jenevil V. Tombaga.
#                       """)
# print(response)

# print("Here is the conversation with template but with user and chatbot history \\n")
# print(conversation)

#can delete/edit role: system basically the template by del conversation[0] or conversation[0]['content'] = new template
# del conversation[0]
conversation[0]['content'] = """new template"""

# print("Here is the conversation without template but with user and chatbot history \n")
# print(conversation)