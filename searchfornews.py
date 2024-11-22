import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk
import joblib
import time
import requests
from io import BytesIO
from model import preprocess_text
from news_extract import *
from news_scrape import *
from news_nlp import *

# Load the trained model, TF-IDF vectorizer, and label encoder
best_model = joblib.load('best_model.pkl')
tfidf = joblib.load('tfidf_vectorizer.pkl')
label_encoder = joblib.load('label_encoder.pkl')

# Define the predict_category function
def predict_category(new_headline):
    new_cleaned_text = preprocess_text(new_headline)
    new_tfidf = tfidf.transform([new_cleaned_text])
    predicted_category = best_model.predict(new_tfidf)
    predicted_category_label = label_encoder.inverse_transform(predicted_category)
    return predicted_category_label[0]

def retrieve_article(name_entry, interest_entry):
    if not name_entry or not interest_entry:
        messagebox.showwarning("Input Error", "Please enter your name and interested news.")
        return

    predicted_category = predict_category(interest_entry).lower()
    my_url = "https://www.nytimes.com/section/" + predicted_category

    output_area.delete(1.0, tk.END)  # Clear the output area
    output_area.insert(tk.END, f"Welcome {name_entry}! Retrieving articles in the '{predicted_category}' category...\n")
    output_area.insert(tk.END, "Extracting article hyperlinks...\n")
    time.sleep(1)  # Simulate loading time
    output_area.insert(tk.END, "Retrieving summaries...\n")
    time.sleep(1)

    try:
        content_string = get_content_string(my_url)
        starts, ends = find_occurrences(content_string)
        url_list = get_all_urls(starts, ends, content_string)

        if not url_list:
            output_area.insert(tk.END, "No articles found.\n")
            return

        # Clear previous images
        for widget in image_frame.winfo_children():
            widget.destroy()

        for url in url_list:
            output_area.insert(tk.END, f"Article URL: {url}\n")
            article_summary, authorName, PublishDate = summarize_article(url)
            polarity, subjective = find_sentiment(article_summary)

            # Get the article image URL
            image_url = get_image_url(url)  # Implement this function to extract the image URL from the article
            print(f"Retrieved Image URL: {image_url}")  # Debugging print statement

            if image_url:
                show_image(image_url)

            output_area.insert(tk.END, f"Author name: {authorName}\n Published Date: {PublishDate}\n Summary: {article_summary}\nFINAL ANALYSIS:\n---------------------------\n Polarity: {polarity}\n Subjectivity: {subjective}")
            output_area.insert(tk.END, "------------------------------------------------\n")
            output_area.update()  # Update the output area
            time.sleep(2)  # Allows user to read through the text

        output_area.insert(tk.END, f"The articles have been successfully extracted! In total, {len(url_list)} articles were extracted.\n")
        output_area.insert(tk.END, f"Thanks for participating, {name_entry}!\n")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing articles: {e}")

def show_image(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Check for HTTP errors
        img_data = Image.open(BytesIO(response.content))
        img_data = img_data.resize((300, 200))  # Resize the image
        img = ImageTk.PhotoImage(img_data)

        # Create a label to display the image
        img_label = tk.Label(image_frame, image=img)
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack(pady=5)
        print("Image displayed successfully.")  # Debugging print statement

    except Exception as e:
        output_area.insert(tk.END, f"Could not load image: {e}\n")
        print(f"Error loading image: {e}")  # Debugging print statement

def get_image_url(article_url):
    # Dummy implementation, replace this with actual logic to extract image URLs
    # For example, you can use BeautifulSoup to parse the article HTML and find the image tags.
    return article_url  #"https://static01.nyt.com/images/2024/10/23/business/00dc-intel/00dc-intel-facebookJumbo.jpg"  # Replace with actual image URL extraction logic

# Setting up the main window
window = tk.Tk()
window.title("Newspaper Scrape Project")
window.geometry("700x600")
window.configure(bg="#f0f0f0")  # Light gray background

# Title
title_label = tk.Label(window, text="Newspaper Scrape Project", font=("Arial", 18, "bold"), bg="#f0f0f0")
title_label.pack(pady=10)

# Welcome message
welcome_label = tk.Label(window, text="Welcome to the Newspaper Scrape Project!", font=("Arial", 14), bg="#f0f0f0")
welcome_label.pack(pady=5)

# User name input
name_frame = tk.Frame(window, bg="#f0f0f0")
name_frame.pack(pady=10)
tk.Label(name_frame, text="Enter your name:", bg="#f0f0f0").pack(side=tk.LEFT)
name_entry = tk.Entry(name_frame, width=40)
name_entry.pack(side=tk.LEFT, padx=5)

# User interest input
interest_frame = tk.Frame(window, bg="#f0f0f0")
interest_frame.pack(pady=10)
tk.Label(interest_frame, text="What are you looking for today?", bg="#f0f0f0").pack(side=tk.LEFT)
interest_entry = tk.Entry(interest_frame, width=40)
interest_entry.pack(side=tk.LEFT, padx=5)

# Retrieve articles button
retrieve_button = tk.Button(window, text="Retrieve Articles", command=lambda: retrieve_article(name_entry.get(), interest_entry.get()), bg="#4CAF50", fg="white", font=("Arial", 12))
retrieve_button.pack(pady=20)

# Output area
output_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=70, height=20, font=("Arial", 10))
output_area.pack(pady=10)

# Frame for images
image_frame = tk.Frame(window)
image_frame.pack(pady=10)

# Start the GUI main loop
window.mainloop()


