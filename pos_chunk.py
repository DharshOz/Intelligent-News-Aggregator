import nltk
import os

# Set the NLTK data path
nltk_data_path = r"D:\NLP\NewspaperScrape\nlp_env\nltk_data"
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)

# Add the custom NLTK data path
nltk.data.path.append(nltk_data_path)

# Download the necessary NLTK resources
nltk.download('maxent_ne_chunker_tab', download_dir=nltk_data_path)
nltk.download('punkt', download_dir=nltk_data_path)
nltk.download('averaged_perceptron_tagger_eng', download_dir=nltk_data_path)
nltk.download('words', download_dir=nltk_data_path)  # Add this line to download 'words'

from nltk import pos_tag, word_tokenize, RegexpParser

# Mapping of POS tags to their full forms
pos_full_forms = {
    'CC': 'Coordinating conjunction',
    'CD': 'Cardinal number',
    'DT': 'Determiner',
    'EX': 'Existential there',
    'FW': 'Foreign word',
    'IN': 'Preposition or subordinating conjunction',
    'JJ': 'Adjective',
    'JJR': 'Adjective, comparative',
    'JJS': 'Adjective, superlative',
    'LS': 'List item marker',
    'MD': 'Modal',
    'NN': 'Noun, singular or mass',
    'NNS': 'Noun, plural',
    'NNP': 'Proper noun, singular',
    'NNPS': 'Proper noun, plural',
    'PDT': 'Predeterminer',
    'POS': 'Possessive ending',
    'PRP': 'Personal pronoun',
    'PRP$': 'Possessive pronoun',
    'RB': 'Adverb',
    'RBR': 'Adverb, comparative',
    'RBS': 'Adverb, superlative',
    'RP': 'Particle',
    'TO': 'to',
    'UH': 'Interjection',
    'VB': 'Verb, base form',
    'VBD': 'Verb, past tense',
    'VBG': 'Verb, gerund or present participle',
    'VBN': 'Verb, past participle',
    'VBP': 'Verb, non-3rd person singular present',
    'VBZ': 'Verb, 3rd person singular present',
    'WDT': 'Wh-determiner',
    'WP': 'Wh-pronoun',
    'WP$': 'Possessive wh-pronoun',
    'WRB': 'Wh-adverb',
}

def tag_and_chunk(user_input):
    # Tokenize the input query
    tokens = word_tokenize(user_input)
    
    # Part-of-speech tagging
    tagged = pos_tag(tokens)
    
    # Define a grammar for chunking (Noun Phrase Chunking)
    grammar = r"""
      NP: {<DT>?<JJ>*<NN.*>}  # Noun phrases
    """
    chunk_parser = RegexpParser(grammar)
    
    # Chunking
    chunks = chunk_parser.parse(tagged)
    
    # Displaying the results
    print("Tokens and POS Tags:")
    for token, tag in tagged:
        full_tag = pos_full_forms.get(tag, tag)  # Get full form or fallback to tag
        print(f"{token}: {full_tag}")
    
    print("\nChunked Noun Phrases:")
    for subtree in chunks.subtrees():
        if subtree.label() == 'NP':
            print(subtree)

    # Named Entity Recognition
    named_entities = nltk.ne_chunk(tagged)
    print("\nNamed Entities:")
    print(named_entities)

#user_query = "Apple is looking at buying a U.K. startup for $1 billion."
# tag_and_chunk(user_query)
