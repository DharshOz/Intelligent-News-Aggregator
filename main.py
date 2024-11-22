# Imports all the methods and variables from each script.
from news_extract import *
from news_scrape import *
from news_nlp import *
import time

# Welcome Messages and Introduction
print("Welcome to the Newspaper Scrape Project. \nIn seconds, you will have access to the latest articles "
      "in the technology section of the New York Times. \nIn addition, you will also be able to know whether the "
      "article is positive or negative and the extent of the writer's bias.")
print()

# Getting the user input; adding an element of personalization!
name = input("Enter your name to get started: ")

# Console Display
print(f"Welcome {name}! \nYou will now see the latest technology articles in the New York Times...")
print("Extracting article hyperlinks...")
time.sleep(2)
print("Retrieving summaries...")
print()
time.sleep(2)


import joblib
from model import preprocess_text  # Assuming the preprocess function is in the same module

# Load the trained model, TF-IDF vectorizer, and label encoder
best_model = joblib.load('best_model.pkl')
tfidf = joblib.load('tfidf_vectorizer.pkl')
label_encoder = joblib.load('label_encoder.pkl')

# Define the predict_category function
def predict_category(new_headline):
    # Preprocess the new headline
    new_cleaned_text = preprocess_text(new_headline)
    
    # Transform the headline using the trained TF-IDF vectorizer
    new_tfidf = tfidf.transform([new_cleaned_text])

    # Predict the category for the new headline
    predicted_category = best_model.predict(new_tfidf)
    
    # Get the predicted category label
    predicted_category_label = label_encoder.inverse_transform(predicted_category)
    
    return predicted_category_label[0]

# Example 
user_interest = input("What you are looking for today: ")

predicted_category = predict_category(user_interest)
#print(f"Predicted Category: {predicted_category}")

predicted_category = predicted_category.lower()
# Modify to use the correct Technology section URL.
my_url = "https://www.nytimes.com/section/" + predicted_category
#my_url = "https://timesofindia.indiatimes.com/sports/cricket"
try:
    # Gets all the latest URLs from the NY Times Technology Section. (see news_extract.py for more detail)
    content_string = get_content_string(my_url)
    starts, ends = find_occurrences(content_string)
    url_list = get_all_urls(starts, ends, content_string)

    # Ensure URLs were found
    if len(url_list) == 0:
        print("No articles found.")
    
    # Get the article summary and perform sentiment analysis for each URL
    for url in url_list:
        print(f"Article URL: {url}")
        article_summary = summarize_article(url)
        find_sentiment(article_summary)
        print("------------------------------------------------")
        time.sleep(5)  # Allows user to read through all the text.

except Exception as e:
    print(f"An error occurred while processing articles: {e}")

# Closing Messages

print(f"The articles have been successfully extracted! In total, {len(url_list)} articles were extracted.")
print(f"Thanks for participating, {name}!")
