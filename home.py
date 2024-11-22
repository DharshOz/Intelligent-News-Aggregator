import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk
import joblib
import time
import requests
from io import BytesIO
import mysql.connector  # MySQL connector import
from model import preprocess_text
from news_extract import *
from news_scrape import *
from news_nlp import *
import nltk
from pos_chunk import *
# Connect to MySQL
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mysql#rjd22004",
            database="criminal"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error connecting to the database: {err}")
        return None

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

# Function to check if username exists in the login1 table
def username_exists(name_entry):
    connection = connect_to_db()
    if not connection:
        return False
    cursor = connection.cursor()
    cursor.execute("SELECT Username FROM login1 WHERE Username = %s", (name_entry,))
    result = cursor.fetchone()
    connection.close()
    return result is not None

# Store the search query and predicted category into the knowledgebase table
def store_to_knowledgebase(name_entry, predicted_category_label, query_label):
    connection = connect_to_db()
    if not connection:
        return
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO knowledgebase (category, search, username) VALUES (%s, %s, %s)",
        (predicted_category_label, query_label,name_entry)
    )
    connection.commit()
    connection.close()

# Function to retrieve articles
def retrieve_article(name_entry, interest_entry):
    tag_and_chunk(interest_entry)
    if not name_entry or not interest_entry:
        messagebox.showwarning("Input Error", "Please enter your name and interested news.")
        return

    # Check if the user exists in the database
    if not username_exists(name_entry):
        messagebox.showwarning("User Error", f"Username '{name_entry}' does not exist.")
        return

    predicted_category = predict_category(interest_entry).lower()

    # Store the search and predicted category to knowledgebase
    store_to_knowledgebase(name_entry, predicted_category, interest_entry)

    my_url = "https://www.nytimes.com/section/" + predicted_category

    scrollable_text.delete(1.0, tk.END)  # Clear the output area
    scrollable_text.insert(tk.END, f"Welcome {name_entry}! Retrieving articles in the '{predicted_category}' category...\n")
    scrollable_text.insert(tk.END, "Extracting article hyperlinks...\n")
    time.sleep(1)  # Simulate loading time
    scrollable_text.insert(tk.END, "Retrieving summaries...\n")
    time.sleep(1)
    process(my_url)

import mysql.connector
from tkinter import messagebox

def get_user_categories():
    # Check if the user entered the username
    username = name_entry.get()
    #tag_and_chunk(username)
    if not username:
        messagebox.showwarning("Input Error", "Please enter your username.")
        return

    try:
        # Establish MySQL connection
        db_conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mysql#rjd22004",
            database="criminal"
        )
        cursor = db_conn.cursor()

        # Query to get all categories and their frequencies for the user
        query = """
        SELECT category, COUNT(category) as frequency
        FROM knowledgebase
        WHERE Username = %s
        GROUP BY category
        ORDER BY frequency DESC;
        """
        cursor.execute(query, (username,))
        categories = cursor.fetchall()

        # Close the connection
        cursor.close()
        db_conn.close()

        if not categories:
            messagebox.showinfo("No Categories", "No categories found for this user.")
            return

        # Process each category, scraping more articles for higher frequency categories
        total_articles = 20  # Total number of articles to scrape
        for idx, (category, frequency) in enumerate(categories):
            # Allocate a proportional number of articles based on frequency
            articles_to_scrape = (total_articles // len(categories)) + idx  # Higher frequency gets more articles
            my_url = "https://www.nytimes.com/section/" + category.lower()

            # Call the process function to scrape articles
            for _ in range(articles_to_scrape):
                process1(my_url)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"An error occurred: {err}")








# The process and show_image functions remain unchanged
def process(my_url):
    try:
        content_string = get_content_string(my_url)
        starts, ends = find_occurrences(content_string)
        url_list = get_all_urls(starts, ends, content_string)
        scrollable_text.delete(1.0, tk.END) 

        if not url_list:
            scrollable_text.insert(tk.END, "No articles found.\n")
            return

        # Clear previous images
        for widget in image_frame.winfo_children():
            widget.destroy()

        for url in url_list:
            # Check if the URL is valid
            if not url.startswith('http'):
                #scrollable_text.insert(tk.END, f"Invalid URL: {url}\n")
                continue  # Skip invalid URLs

            scrollable_text.insert(tk.END, f"Article URL: {url}\n")
            try:
                article_summary, authorName, PublishDate, image = summarize_article(url)
                polarity, subjective = find_sentiment(article_summary)

                # Validate image URL
                if image and image.startswith('http'):
                    show_image(image)
                else:
                    scrollable_text.insert(tk.END, "Image URL invalid or missing.\n")

                # Format the summary and details
                scrollable_text.insert(tk.END, f"Author: {authorName}\n"
                                                 f"Published Date: {PublishDate}\n"
                                                 f"Summary: {article_summary}\n"
                                                 f"FINAL ANALYSIS:\n"
                                                 f"---------------------------\n"
                                                 f"Polarity: {polarity}\n"
                                                 f"Subjectivity: {subjective}\n")
                scrollable_text.insert(tk.END, "==============================================================================\n")
            except Exception as e:
                scrollable_text.insert(tk.END, f"Error processing article: {e}\n")
            
            scrollable_text.update()  # Update the output area
            time.sleep(2)  # Allows user to read through the text

        scrollable_text.insert(tk.END, f"The articles have been successfully extracted! In total, {len(url_list)} articles were extracted.\n")
        scrollable_text.insert(tk.END, f"Thanks for participating, {name_entry}!\n")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing articles: {e}")

def process1(my_url):
    try:
        content_string = get_content_string(my_url)
        starts, ends = find_occurrences(content_string)
        url_list = get_all_urls(starts, ends, content_string)

        if not url_list:
            scrollable_text.insert(tk.END, "No articles found.\n")
            return

        # Clear previous images
        for widget in image_frame.winfo_children():
            widget.destroy()

        for url in url_list:
            # Check if the URL is valid
            if not url.startswith('http'):
                #scrollable_text.insert(tk.END, f"Invalid URL: {url}\n")
                continue  # Skip invalid URLs

            scrollable_text.insert(tk.END, f"Article URL: {url}\n")
            try:
                article_summary, authorName, PublishDate, image = summarize_article(url)
                polarity, subjective = find_sentiment(article_summary)

                # Validate image URL
                if image and image.startswith('http'):
                    show_image(image)
                else:
                    scrollable_text.insert(tk.END, "Image URL invalid or missing.\n")

                # Format the summary and details
                formatted_output = (
                    f"Author: {authorName}\n"
                    f"Published Date: {PublishDate}\n"
                    f"Summary: {article_summary}\n"
                    f"FINAL ANALYSIS:\n"
                    f"---------------------------\n"
                    f"Polarity: {polarity}\n"
                    f"Subjectivity: {subjective}\n"
                    "===========================================================================================\n"
                )
                scrollable_text.insert(tk.END, formatted_output)
            except Exception as e:
                scrollable_text.insert(tk.END, f"Error processing article: {e}\n")
            
            scrollable_text.update()  # Update the output area
            time.sleep(2)  # Allows user to read through the text

        scrollable_text.insert(tk.END, f"The articles have been successfully extracted! In total, {len(url_list)} articles were extracted.\n")
        scrollable_text.insert(tk.END, f"Thanks for participating, {name_entry}!\n")

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
        scrollable_text.insert(tk.END, f"Could not load image: {e}\n")
        print(f"Error loading image: {e}")  # Debugging print statement






# Start the main loop




def latestNews():
    my_url = "https://www.nytimes.com"
    process(my_url)

from chatbot import *
def bot():
    bot_result = main(query_entry.get())
    scrollable_text.delete(1.0, tk.END)

    scrollable_text.insert(tk.END, f"BOT RESULT: {bot_result}\n")


# Create the main window
root = tk.Tk()
root.title("INTELLIGENT NEWS AGGREGATOR")
root.geometry("1366x768")



# Title label at the top
title_label = tk.Label(root, text="INTELLIGENT NEWS AGGREGATOR", font=("Helvetica", 24, "bold"), bg="black", fg="white")
title_label.pack(side="top", fill="x")

# Left frame for buttons and inputs
left_frame = tk.Frame(root, width=300, height=768, bg="black")
left_frame.pack(side="left", fill="y")

# Right frame for chat (with scrollbar)
right_frame = tk.Frame(root, bg="grey")
right_frame.pack(side="right", fill="both", expand=True)

scrollable_text = scrolledtext.ScrolledText(right_frame, wrap="word", bg="#EDEDED", fg="black", font=("Helvetica", 12), padx=10, pady=10)
scrollable_text.pack(fill="both", expand=True)

# Create labels and entry fields
name_label = tk.Label(left_frame, text="Enter your name:", font=("Helvetica", 12), bg="black", fg="white")
name_label.pack(pady=(20, 5))

name_entry = tk.Entry(left_frame, font=("Helvetica", 12), width=25)
name_entry.pack(pady=5)

query_label = tk.Label(left_frame, text="What are you looking for?", font=("Helvetica", 12), bg="black", fg="white")
query_label.pack(pady=5)

query_entry = tk.Entry(left_frame, font=("Helvetica", 12), width=25)
query_entry.pack(pady=5)

# Button properties
button_width = 20
button_height = 2
button_font = ("Helvetica", 14)

# Create empty buttons on the left frame
chatbot_button = tk.Button(left_frame, text="SEARCH", command=lambda: retrieve_article(name_entry.get(), query_entry.get()), width=button_width, height=button_height, font=button_font, bg='red')
chatbot_button.pack(pady=20)

categories_button = tk.Button(left_frame, text="chatbot",command= bot, width=button_width, height=button_height, font=button_font, bg='red')
categories_button.pack(pady=20)

latest_news_button = tk.Button(left_frame, text="Latest News", command=latestNews, width=button_width, height=button_height, font=button_font, bg='red')
latest_news_button.pack(pady=20)

favourite_news_button =  tk.Button(left_frame, text="Your Favourites", command=get_user_categories, width=button_width, height=button_height, font=button_font, bg='red')
favourite_news_button.pack(pady=20)
"""
# Create a frame to hold the canvas and scrollbar
image_container = tk.Frame(root)
image_container.pack(pady=10)

# Create a canvas for the image frame
image_canvas = tk.Canvas(image_container)
image_canvas.pack(side=tk.LEFT)

# Create a scrollbar linked to the canvas
image_scrollbar = tk.Scrollbar(image_container, orient="vertical", command=image_canvas.yview)
image_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure the canvas to use the scrollbar
image_canvas.configure(yscrollcommand=image_scrollbar.set)

# Create a frame for the images
image_frame = tk.Frame(image_canvas)

# Add the image frame to the canvas
image_canvas.create_window((0, 0), window=image_frame, anchor='nw')

# Function to resize the canvas and update the scrollbar
def on_frame_configure(event):
    image_canvas.configure(scrollregion=image_canvas.bbox("all"))

# Bind the configure event of the image_frame to the canvas
image_frame.bind("<Configure>", on_frame_configure)

# The rest of your code remains unchanged...
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
        scrollable_text.insert(tk.END, f"Could not load image: {e}\n")
        print(f"Error loading image: {e}")  # Debugging print statement

"""

image_frame = tk.Frame(root)
image_frame.pack(pady=10)

# Start the main loop
root.mainloop()


