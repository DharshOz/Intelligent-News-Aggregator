import requests
from bs4 import BeautifulSoup
from newspaper import Article
from PIL import Image
from io import BytesIO

def scrape_google_news():
    print("Scraping news from Google News...")
    url = "https://news.google.com/rss"  # Google News RSS feed URL
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve data from Google News.")
        return []

    soup = BeautifulSoup(response.content, 'xml')  # Parse as XML for RSS feed
    articles = soup.find_all('item')

    if not articles:
        print("No news found for Google News.")
        return []
    
    news_items = [(article.title.text, article.link.text) for article in articles]
    return news_items

def fetch_image_and_full_text(link):
    print(f"Fetching image and full text from article: {link}")
    article = Article(link)
    article.download()
    article.parse()
    
    # Extract the first image
    image_url = list(article.images)[0] if article.images else None
    full_text = article.text  # Extract the full text of the article
    
    return image_url, full_text

def show_image(image_url):
    if image_url:
        try:
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            img.show()  # Open the image in the default image viewer
        except Exception as e:
            print(f"Could not open image {image_url}: {e}")
    else:
        print("No image found for this article.")

def main():
    google_news = scrape_google_news()
    if google_news:
        print("Google News:")
        for title, link in google_news[:10]:  # Limit to the first 10 articles
            print(f"- {title} ({link})\n")  # Print title and link with spacing
            image_url, full_text = fetch_image_and_full_text(link)  # Fetch the first image and full text for the article
            show_image(image_url)  # Show the image
            
            # Print the full text, ensuring at least 500 words are printed
            full_text_words = full_text.split()
            if len(full_text_words) >= 500:
                print("Summary (first 500 words):")
                print(" ".join(full_text_words[:500]))
            else:
                print("Full Text (less than 500 words):")
                print(full_text)

            print("\n" + "="*80 + "\n")  # Separator for clarity

if __name__ == "_main_":
    main()