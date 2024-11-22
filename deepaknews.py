import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize
import requests

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Function to fetch news articles for a given country (India)
def fetch_news(category='general'):
    api_key = "e4183d2e99f7464b97f104df59e4a9a7" # Replace with your actual News API key
    if category == 'general':
        news_url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    else:
        news_url = f"https://newsapi.org/v2/top-headlines?category={category}&country=in&apiKey={api_key}"
    
    response = requests.get(news_url)
    articles = response.json().get('articles', [])
    return articles

# Function to analyze user input and decide on action
def analyze_input(user_input):
    user_input = user_input.lower()
    keywords = {
        "summary": ["tell", "show", "give", "provide", "describe"],
        "headlines": ["list", "show", "display", "present"],
        "details": ["detail", "information", "more about"],
        "latest": ["latest", "newest", "recent"],
        "headlines_only": ["headlines", "just the headlines", "only headlines"]
    }

    for action, phrases in keywords.items():
        if any(phrase in user_input for phrase in phrases):
            return action
    return "unknown"

# Function to extract category from user input
def extract_category(user_input):
    categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
    for category in categories:
        if category in user_input.lower():
            return category
    return "general"  # Default category

# Function to display news based on user request
def display_news(action, category):
    articles = fetch_news(category)

    if action in ["summary", "details"]:
        for article in articles:
            print("Title:", article['title'])
            print("Summary:", article['description'])
            print("Link:", article['url'])
            print("\n")
    elif action in ["headlines", "headlines_only"]:
        print(f"Today's {category.capitalize()} News Headlines:")
        for article in articles:
            print("-", article['title'])
    elif action == "latest":
        print(f"Latest {category.capitalize()} News:")
        for article in articles:
            print("Title:", article['title'])
            print("Link:", article['url'])
            print("\n")
    else:
        print("Sorry, I didn't understand that.")

# Main function to run the news aggregator
def main():
    user_input = input("Please enter your request (e.g., 'tell me today's sports news' or 'list the technology news'): ")
    category = extract_category(user_input)
    action = analyze_input(user_input)
    display_news(action, category)

if __name__ == "__main__":
    main()
