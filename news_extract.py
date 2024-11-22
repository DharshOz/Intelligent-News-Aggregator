# Description: This script extracts ALL the latest articles from the technology section of the New York Times with
# BeautifulSoup.

import requests
from bs4 import BeautifulSoup as soup

def get_content_string(url):
    page = requests.get(url)
    page_soup = soup(page.content, 'html.parser')
    # Use the below statement as a visualizer of the HTML outline.
    containers = page_soup.find_all("script", {"type": "application/ld+json"})

    if not containers:
        raise ValueError("No valid script tags with type application/ld+json found.")
    
    article_list = []
    for container in containers:
        try:
            for dictionary in container:
                article_list.append(dictionary)
        except Exception as e:
            print(f"Error while processing JSON structure: {e}")

    if len(article_list) < 2:
        raise ValueError("Insufficient data in article list for processing.")
    
    article_list[0:2] = [''.join(article_list[0:2])]
    content_string = article_list[0]
    
    if "itemListElement" not in content_string:
        raise ValueError("itemListElement not found in content string.")
    
    article_index = content_string.index("itemListElement")
    content_string = content_string[article_index + 18:]
    return content_string

def find_occurrences(content_string):
    start_indices = [i for i in range(len(content_string)) if content_string.startswith('https://www.nytimes.com/2024', i)]
    end_indices = [i for i in range(len(content_string)) if content_string.startswith('.html', i)]
    end_indices = [x + 5 for x in end_indices]

    # Ensure both lists are the same size
    if len(start_indices) > len(end_indices):
        start_indices = start_indices[:len(end_indices)]
    if len(end_indices) > len(start_indices):
        end_indices = end_indices[:len(start_indices)]
        
    return start_indices, end_indices

def get_all_urls(start_indices, end_indices, content_string):
    url_list = []
    for i in range(len(start_indices)):
        url_list.append(content_string[start_indices[i]:end_indices[i]])
    return url_list
