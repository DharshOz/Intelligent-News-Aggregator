import tkinter as tk
import pandas as pd
from textblob import TextBlob
from transformers import pipeline
import json
from tkinter import scrolledtext
from newspaper import Article
import requests
from bs4 import BeautifulSoup
from searchfornews import  retrieve_article
import subprocess

class NewsAggregatorApp:
    def __init__(self, master, categories, data):
        self.master = master
        self.master.title("INTELLIGENT NEWS AGGREGATOR")
        self.master.geometry("1366x768")

        # Title label at the top
        self.title_label = tk.Label(master, text="INTELLIGENT NEWS AGGREGATOR", font=("Helvetica", 24, "bold"), bg="black", fg="white")
        self.title_label.pack(side="top", fill="x")

        # Left frame for buttons
        self.left_frame = tk.Frame(master, width=300, height=768, bg="black")
        self.left_frame.pack(side="left", fill="y")

        # Right frame for chat (with scrollbar)
        self.right_frame = tk.Frame(master, bg="grey")
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.scrollable_text = scrolledtext.ScrolledText(self.right_frame, wrap="word", bg="#EDEDED", fg="black", font=("Helvetica", 12), padx=10, pady=10)
        self.scrollable_text.pack(fill="both", expand=True)

        # Buttons on the left frame
        button_width = 20
        button_height = 2
        button_font = ("Helvetica", 14)

        self.chatbot_button = tk.Button(self.left_frame, text="Chat Bot News", command=self.open_chatbot_page, width=button_width, height=button_height, font=button_font, bg='red')
        self.chatbot_button.pack(pady=20)

        self.categories_button = tk.Button(self.left_frame, text="Show Categories", command=self.show_categories_popup, width=button_width, height=button_height, font=button_font, bg='red')
        self.categories_button.pack(pady=20)

        self.latest_news_button = tk.Button(self.left_frame, text="Latest News", command=self.scrape_latest_news, width=button_width, height=button_height, font=button_font, bg='red')
        self.latest_news_button.pack(pady=20)

        self.search_news_button = tk.Button(self.left_frame, text="Search News", command=self.open_search_window, width=button_width, height=button_height, font=button_font, bg='red')
        self.search_news_button.pack(pady=20)

        self.categories = categories
        self.data = data

    def open_chatbot_page(self):
        self.scrollable_text.delete('1.0', tk.END)

        # Chat-like bubble for user query
        self.scrollable_text.insert(tk.END, "\n\n")  # Add some spacing

        # User's input section (WhatsApp style)
        self.query_label = tk.Label(self.scrollable_text, text="You:", font=("Helvetica", 12), bg="#DCF8C6", anchor="w", width=30, padx=10, pady=5)
        self.scrollable_text.window_create(tk.END, window=self.query_label)
        self.scrollable_text.insert(tk.END, "\n")

        self.query_entry = tk.Entry(self.scrollable_text, width=70, font=("Helvetica", 12))
        self.scrollable_text.window_create(tk.END, window=self.query_entry)
        self.scrollable_text.insert(tk.END, "\n")

        # 'Send' button resembling WhatsApp chat button
        self.send_button = tk.Button(self.scrollable_text, text="Send", command=self.predict_category, bg="#25D366", fg="white", font=("Helvetica", 12), padx=10, pady=5)
        self.scrollable_text.window_create(tk.END, window=self.send_button)
        self.scrollable_text.insert(tk.END, "\n\n")

        self.result_label = tk.Label(self.scrollable_text, text="", font=("Helvetica", 12), bg="#ECECEC", fg="black", padx=10, pady=5)
        self.scrollable_text.window_create(tk.END, window=self.result_label)

    def predict_category(self):
        query = self.query_entry.get()

        # Add user query as a bubble
        user_bubble = f'You: {query}'
        self.scrollable_text.insert(tk.END, f'\n\n{user_bubble}\n', 'user')
        self.scrollable_text.tag_config('user', background="#DCF8C6", foreground="black", justify='left', lmargin1=10, lmargin2=10, rmargin=30)

        sentiment_score, category = self.analyze_sentiment_and_classify(query)
        response_bubble = f'Bot: Predicted Category: {category} | Sentiment Score: {sentiment_score:.2f}'

        # Display bot's response as a chat bubble
        self.scrollable_text.insert(tk.END, f'\n\n{response_bubble}\n', 'bot')
        self.scrollable_text.tag_config('bot', background="#ECECEC", foreground="black", justify='right', lmargin1=30, lmargin2=10, rmargin=10)

        self.scrollable_text.see(tk.END)  # Scroll to the end

    def analyze_sentiment_and_classify(self, query):
        analysis = TextBlob(query)
        sentiment = analysis.sentiment.polarity
        classification = model(query, self.categories)
        predicted_category = classification['labels'][0]
        return sentiment, predicted_category

    def show_categories_popup(self):
        self.scrollable_text.delete('1.0', tk.END)
        categories_str = "\n".join(self.categories)

        self.categories_label = tk.Label(self.scrollable_text, text="Available News Categories:", font=("Helvetica", 14), bg="grey", fg="white")
        self.scrollable_text.window_create(tk.END, window=self.categories_label)
        self.scrollable_text.insert(tk.END, "\n")

        self.categories_list = tk.Label(self.scrollable_text, text=categories_str, font=("Helvetica", 12), bg="grey", fg="white")
        self.scrollable_text.window_create(tk.END, window=self.categories_list)

    def scrape_latest_news(self):
        self.scrollable_text.delete('1.0', tk.END)

        # News scraping using BeautifulSoup or Newspaper3k
        news_sites = {
            "Times of India": "https://timesofindia.indiatimes.com/",
            "The Hindu": "https://www.thehindu.com/",
        }

        for source, url in news_sites.items():
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            headlines = []
            if source == "Times of India":
                for headline in soup.select(".w_tle a"):
                    headlines.append(headline.text.strip())
            elif source == "The Hindu":
                for headline in soup.select("a.story-card75x1-text"):
                    headlines.append(headline.text.strip())

            # Display the news source and its headlines in the chat
            self.scrollable_text.insert(tk.END, f'\n\nSource: {source}\n', 'source')
            self.scrollable_text.tag_config('source', background="#ECECEC", foreground="black", font=("Helvetica", 14, "bold"))

            for headline in headlines[:5]:  # Limiting to the first 5 headlines
                self.scrollable_text.insert(tk.END, f'• {headline}\n', 'headline')
                self.scrollable_text.tag_config('headline', background="#ECECEC", foreground="black", justify='left', lmargin1=10, lmargin2=10)

        self.scrollable_text.see(tk.END)

    def open_search_window(self):
        subprocess.run(["python", "searchfornews.py"]) 
        """
        # Create a new window for user input
        search_window = tk.Toplevel(self.master)
        search_window.title("Search News")
        search_window.geometry("400x300")

        title_label = tk.Label(search_window, text="Newspaper Scrape Project", font=("Arial", 18, "bold"), bg="#f0f0f0")
        title_label.pack(pady=10)

        # Welcome message
        welcome_label = tk.Label(search_window, text="Welcome to the Newspaper Scrape Project!", font=("Arial", 14), bg="#f0f0f0")
        welcome_label.pack(pady=5)

        # User name input
        name_frame = tk.Frame(search_window, bg="#f0f0f0")
        name_frame.pack(pady=10)
        tk.Label(name_frame, text="Enter your name:", bg="#f0f0f0").pack(side=tk.LEFT)
        name_entry = tk.Entry(name_frame, width=40)
        name_entry.pack(side=tk.LEFT, padx=5)

        # User interest input
        interest_frame = tk.Frame(search_window, bg="#f0f0f0")
        interest_frame.pack(pady=10)
        tk.Label(interest_frame, text="What are you looking for today?", bg="#f0f0f0").pack(side=tk.LEFT)
        interest_entry = tk.Entry(interest_frame, width=40)
        interest_entry.pack(side=tk.LEFT, padx=5)

        # Retrieve articles button
        retrieve_button = tk.Button(search_window, text="Retrieve Articles", command=retrieve_article(), bg="#4CAF50", fg="white", font=("Arial", 12))
        retrieve_button.pack(pady=20)
        """
    

if __name__ == "__main__":
    json_path = r"C:\Users\adeep\Downloads\archive (1)\News_Category_Dataset_v3_ordered.json"
    with open(json_path, 'r') as f:
        dataset = json.load(f)

    categories = list(set(item['category'] for item in dataset))
    data = pd.DataFrame(dataset)

    model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    root = tk.Tk()
    app = NewsAggregatorApp(root, categories, data)
    root.mainloop()



