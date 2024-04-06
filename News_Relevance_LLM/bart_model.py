from transformers import pipeline
from datetime import datetime
import pandas as pd
import os


# Read the CSV file into a DataFrame
df = pd.read_csv('news relevancy - api_data.csv')

#Pipeline defined and labels are defined
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
category_labels = ['AI', 'Quantum Computing', 'Green Computing', 'Robotics', 'Trust Technologies','Anti-disinformation technologies', 
                   'Communications Technologies', 'General', 'Business', 'Finance']

"""
start = datetime.now()
end = datetime.now()
result = classifier(text, candidate_labels)
td = (end - start).total_seconds() * 10**3
print(td)
"""
#Def bart apply to be used for pandas apply function
def bart_apply(x):
    result = classifier(x,category_labels)
    return result["labels"][0]


df['bart_cat'] = df['Article'].apply(bart_apply)

#print(df['bart_cat'])

#a =  bart_apply(df['Article'][3])

column_to_export = df['bart_cat']

# Export the column to a CSV file
column_to_export.to_csv('bart_column_updated.csv', index=False)

print("Column exported successfully.")
