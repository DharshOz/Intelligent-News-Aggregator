# Description: This program performs sentiment analysis on news articles using TextBlob.
from textblob import TextBlob

# Method Purpose: Given a news summary, ----------------------------------------------------------------extracts polarity and subjectivity metrics, returning both in a readable format.
def find_sentiment(news_story):
    if not news_story or news_story == "Error in summarizing article.":
        print("No valid news story to analyze.")
        return
    
    news = TextBlob(news_story)
    
    # Collect polarity and subjectivity for each sentence.
    polarity_data = []
    subjectivity_data = []
    
    for sentence in news.sentences:
        sentiment = sentence.sentiment
        polarity_data.append(sentiment.polarity)
        subjectivity_data.append(sentiment.subjectivity)

    # The averages of both sentiment lists are calculated.
    polarity_average = calculate_average(polarity_data)
    subjectivity_average = calculate_average(subjectivity_data)

    # Displays the sentiment that relates to the averages on the console.
    print()
    print("FINAL ANALYSIS")
    print("----------------------------------")
    print("Polarity: " + calculate_sentiment(polarity_average, "polarity"))
    print("Subjectivity: " + calculate_sentiment(subjectivity_average, "subjectivity"))
    return calculate_sentiment(polarity_average, "polarity"), calculate_sentiment(subjectivity_average, "subjectivity")

# Helper Methods (for the find_sentiment method)
# -------------------------------------------------------------
def calculate_average(values):
    if len(values) == 0:
        return 0
    return sum(values) / len(values)

def calculate_sentiment(sentiment, sentiment_type):
    sentiment_category = "Neutral"
    if sentiment_type == "polarity":
        if sentiment > 0.75:
            sentiment_category = "Extremely positive."
        elif sentiment > 0.5:
            sentiment_category = "Significantly positive."
        elif sentiment > 0.3:
            sentiment_category = "Fairly positive."
        elif sentiment > 0.1:
            sentiment_category = "Slightly positive."
        elif sentiment < -0.1:
            sentiment_category = "Slightly negative."
        elif sentiment < -0.3:
            sentiment_category = "Fairly negative."
        elif sentiment < -0.5:
            sentiment_category = "Significantly negative."
        elif sentiment < -0.75:
            sentiment_category = "Extremely negative."
    elif sentiment_type == "subjectivity":
        if sentiment > 0.75:
            sentiment_category = "Extremely subjective."
        elif sentiment > 0.5:
            sentiment_category = "Fairly subjective."
        elif sentiment > 0.3:
            sentiment_category = "Fairly objective."
        elif sentiment > 0.1:
            sentiment_category = "Extremely objective."
    return sentiment_category
