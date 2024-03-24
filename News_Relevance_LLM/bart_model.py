from transformers import pipeline
from datetime import datetime
import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('news_r.csv')

#Pipeline defined and labels are defined
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
category_labels = ['AI', 'Quantum Computing', 'Green Computing', 'Robotics', 'Trust Technologies','Anti-disinformation technologies', 'Communications Technologies', 'General', 'Business', 'Finance']

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
column_to_export.to_csv('bart_column.csv', index=False)

print("Column exported successfully.")
#predicted_label = result["labels"][0]
#predicted_score = result["scores"][0]

#print(f"Predicted Label: {predicted_label}, Score: {predicted_score}")
##

#TEMPLATE Codes to work on: for future dev

""" 
from transformers import BartTokenizer

tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-mnli")

# Example of tokenizing a single example
text = "This is an example text."
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
from transformers import BartForSequenceClassification, Trainer, TrainingArguments

model = BartForSequenceClassification.from_pretrained("facebook/bart-large-mnli")

# Define your training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
)

# Define your trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset, # Your tokenized training dataset
    eval_dataset=eval_dataset,    # Your tokenized evaluation dataset
)

# Train the model
trainer.train()
# Evaluate the model
trainer.evaluate()

# Use the model for classification
text = "This is a new text to classify."
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
outputs = model(**inputs)
predicted_label = tokenizer.decode(outputs.logits.argmax(-1), skip_special_tokens=True)
 """