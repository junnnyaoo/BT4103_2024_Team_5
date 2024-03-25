from transformers import pipeline
from datetime import datetime
import pandas as pd
import os
from huggingface_hub import login

# login(os.getenv("HF_API_KEY"))

def DeBERTa_Function(article_content):
    # Read the CSV file into a DataFrame
    #df = pd.read_csv('news_r.csv')

    #Pipeline defined and labels are defined
    classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
    category_labels = ['AI', 'Quantum Computing', 'Green Computing', 'Robotics', 'Trust Technologies','Anti-disinformation technologies', 'Communications Technologies', 'General', 'Business', 'Finance']

    #Def bart apply to be used for pandas apply function
    def deberta_apply(x):
        result = classifier(x,category_labels)
        return result["labels"][0]


    article_category = deberta_apply(article_content)
    
    # List of categories to label as 1
    irrelevant_categories = ["Business","General","Finance"]

    if article_content in irrelevant_categories:
        return "Irrelevant"
    else:
        return "Relevant"
    


ab = '''At the same time, violent conflicts have escalated. A recent report found that in 2022 deaths from internal and external conflicts increased 96% from the previous year. The carnage in Israel and Gaza will likely drive these numbers even higher.

What could be the cause of these disturbing trends?

We appear to be in the midst of an era of what I label “defensive nationalism.” Defensive nationalism is a form of national-populism, or a people’s movement focused on protecting the nation against globalizing forces, whether in the form of trade, finance, or immigration.

Defensive nationalist movements emerge when revolutionary changes in transportation and communications shorten time and reduce distance. These globalizing changes produce wealth and internationalism. But they also dramatically disrupt societies, generating widespread unease and apprehension. Populist politicians capitalize on the generalized fear, painting international forces as a threat that must be countered. Economic protectionism is made to seem paramount, diplomacy takes a back seat, and the military becomes the bulwark of the nation.

The result is an inward populist turn that pushes many people toward radical domestic politics and nations towards violence.

Read More: A Make-or-Break Year for Democracy Worldwide'''

start = datetime.now()
print(DeBERTa_Function(ab))
end = datetime.now()
td = (end - start)
print(td)