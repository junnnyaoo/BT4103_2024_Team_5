import os
from langchain.utilities import SQLDatabase 
from langchain.llms import OpenAI
from langchain_experimental.sql import SQLDatabaseChain
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

pg_uri = os.getenv("POSTGRES_PATH") #insert ur postgres path
db = SQLDatabase.from_uri(pg_uri)

llm = OpenAI(temperature = 0.2, verbose = True)
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

def chat_with_sql():
    print("Type 'exit' to quit")

    while True:
        prompt = input("Enter a prompt: ")

        if prompt.lower() == 'exit':
            print('Exiting...')
            break
        else:
            try:

                print(db_chain.run(prompt))
            except Exception as e:
                print(e)
chat_with_sql()
