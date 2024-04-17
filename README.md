# BT4103   
## BT4103 Capstone Team 5 - Tech Scanning and Analysis Tool Powered by Generative AI (IMDA)   
## ChatBot Name: NewsLink

### Project sponsor    

Infocomm Media Development Authority (IMDA)   

### Objectives   

Leverage Generative AI tools to develop a tech analysis chatbot capable of generating and summarizing the latest tech news and articles for its users. 


### Files Information

#### Main Files
app.py - The main file used to run the SlackBot   
newsMongo.py - The file that is used to hold the scrapping functions while being able to pull data from newsAPI when function "articleScrapeAndStore()" is called.

#### Functional Files/ Helper Function Files
newsRev_BART.py
newsRev_DeBERTa.py   
are files that are used for holding the LLMs function on a seperate file.

readDb_Functions.py - the file that is used for retrieval of news articles from MongoDb
blocks.py - the file that contains Slack's message interface blocks

#### Extra Folder
'News_Relevance_LLM' contains the different LLMs used for testing and their evaluation results. It also contains the dataset used for predicting the columns of each 
LLM or GPT used for relevancy prediction.

'Similarity_Check' contains the python notebook that shows how the vector search is used and how we came out with the threshold for the semantic similarity scoring.





   
-Last updated - 17th April 2024
