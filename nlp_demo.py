# Description: This program combines the major principles of natural language processing in a short, 50-line demo!

from textblob import TextBlob
from textblob import Word
import random



def nlp_classification(text):
    # Summary Retrieval with TextBlob
    print("Summary: " + "\n" + text)
    print()
    summary = TextBlob(text)

    # Part of Speech Tagging
    print("POS Tagging: " + str(summary.tags))
    print()

    # Tokenization into words
    print("Words: " + str(summary.words))

    # Word Inflection
    print("Plural of " + summary.words[1] + " --> " + summary.words[1].pluralize())
    print("Singular of " + summary.words[5] + " --> " + summary.words[5].singularize())
    print()

    # Tokenization into sentences
    print("Sentences: " + str(summary.sentences))
    print()

    # Noun Entity Recognition and Chunking
    nouns = []
    for word, tag in summary.tags:
        if tag == "NN":
            nouns.append(word.lemmatize())
    print("This text is about...")
    for item in random.sample(nouns, 5):
        word = Word(item)
        # Lemmatization
        word.lemmatize()
        print(word.pluralize())


nlp_classification(news_summary)
