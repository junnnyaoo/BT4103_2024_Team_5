from transformers import pipeline
from datetime import datetime
import pandas as pd


def bart_Function(article_content):
    # Read the CSV file into a DataFrame
    #df = pd.read_csv('news_r.csv')

    #Pipeline defined and labels are defined
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    category_labels = ['AI', 'Quantum Computing', 'Green Computing', 'Robotics', 'Trust Technologies','Anti-disinformation technologies', 'Communications Technologies', 'General', 'Business', 'Finance']

    #Def bart apply to be used for pandas apply function
    def bart_apply(x):
        result = classifier(x,category_labels)
        return result["labels"][0]


    article_category = bart_apply(article_content)
    
    # List of categories to label as 1
    irrelevant_categories = ["Business","General","Finance"]
    print(article_category)
    if article_category in irrelevant_categories:
        return "Irrelevant"
    else:
        return "Relevant"
    


