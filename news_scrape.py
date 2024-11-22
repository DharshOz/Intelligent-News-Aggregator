# Description: This program scrapes and summarizes news articles from the New York Times.
from newspaper import Article
import nltk
nltk.download('punkt_tab')

# Summarizes the article and provides valuable information regarding the article metadata, including images and
# attributions.
def summarize_article(url):
    article = Article(url)

    try:
        article.download()
        article.parse()
        # Remove incorrect 'download' usage for 'punkt'
        # Punkt is a sentence tokenizer which should be pre-installed separately.
        article.nlp()

        # Gets the author or authors of the article
        author_string = "Author(s): "
        if article.authors:
            for author in article.authors:
                author_string += f"{author}, "
            author_string = author_string.rstrip(", ")
        else:
            author_string += "Unknown"
        print(author_string)

        # Gets the publish date of the article
        date = article.publish_date

        if date:
            print("Publish Date: " + str(date.strftime("%m/%d/%Y")))
        else:
            print("Publish Date: Unknown")

        # Gets the top image of the article
        print(f"Top Image Url: {article.top_image}")

        # Gets the article images
        image_string = "All Images: "
        for image in article.images:
            image_string += f"\n\t{image}"  # adds a newline and a tab before each image is printed
        print(image_string)
        print()

        # Gets the article summary
        print("A Quick Article Summary")
        print("----------------------------------------")
        print(article.summary)

        return article.summary, author_string, str(date.strftime("%m/%d/%Y")), article.top_image

    except Exception as e:
        print(f"Error processing article {url}: {e}")
        return "Error in summarizing article."


