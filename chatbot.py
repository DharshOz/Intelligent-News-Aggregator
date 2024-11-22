import re
import requests
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Load pre-trained GPT-2 model and tokenizer
model_name = 'gpt2'
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Function to clean up "not" statements in the user query
def clean_negation(query):
    cleaned_query = re.sub(r'\bnot\s+\w+\b', '', query, flags=re.IGNORECASE)
    return cleaned_query.strip()

# Function to fetch news from Google News RSS
def fetch_latest_news(query):
    google_news_url = f'https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en'
    response = requests.get(google_news_url)
    if response.status_code != 200:
        return "Couldn't fetch the latest news."
    root = ET.fromstring(response.content)
    items = root.findall(".//item")
    if items:
        first_item = items[0]
        title = first_item.find("title").text
        link = first_item.find("link").text
        return title, link
    else:
        return "No latest news found.", None

# Function to scrape news article content from a given URL
def scrape_news_article(url):
    response = requests.get(url)
    if response.status_code != 200:
        return "Couldn't fetch the article."
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Example of extracting article content; you may need to adjust based on actual HTML structure
    paragraphs = soup.find_all('p')
    content = ' '.join([para.get_text() for para in paragraphs])
    return content

# Function to generate news-based response using GPT-2
def generate_news_response(prompt):
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(inputs, max_new_tokens=100, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Main loop to handle user input
def main(user_input):
    
    while True:
        #user_input = input("You: ")

        if user_input.lower() in ['exit', 'quit']:
            print("Exiting the chatbot. Goodbye!")
            break

        if not user_input.strip():
            print("Please enter a valid query.")
            continue

        # Clean the user input to remove negation terms
        cleaned_query = clean_negation(user_input)

        # Fetch the latest news from Google News
        news_title, news_link = fetch_latest_news(cleaned_query)

        # If news is found, scrape the article content
        if news_link:
            article_content = scrape_news_article(news_link)
            news_data = f"Latest news on {cleaned_query}: {news_title}\n{article_content}"
        else:
            news_data = "No latest news found."
        print("scraped news:",news_data)

        # Generate GPT-2 response
        gpt2_response = generate_news_response(f"News: {cleaned_query}. {news_data}")

        # Display the response in the terminal
        print(f"Bot: {gpt2_response}\n")
        return gpt2_response


#if __name__ == "__main__":
#    main()
