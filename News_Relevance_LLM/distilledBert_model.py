from transformers import pipeline
from datetime import datetime
import pandas as pd

##

# Read the CSV file into a DataFrame
df = pd.read_csv('news_r.csv')
print('1')
#classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased") #Base Model
classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli") #Better Accuracy
print('12')
candidate_labels = ['AI', 'Quantum Computing', 'Green Computing', 'Robotics', 'Trust Technologies','Anti-disinformation technologies', 'Communications Technologies', 'General', 'Business', 'Finance']

df = pd.read_csv('news_r.csv')

def bart_apply(x):
    result = classifier(x,candidate_labels)
    return result["labels"][0]
print('13')
df['bart_cat'] = df['Article'].apply(bart_apply)
print(df['bart_cat'])
#Export the column to a CSV file
column_to_export = df['bart_cat']
column_to_export.to_csv('dBert_column.csv', index=False)

print("Column exported successfully.")