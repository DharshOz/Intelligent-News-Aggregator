# Import necessary libraries
import pandas as pd
import string
import re
import nltk
import warnings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils import class_weight
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import joblib

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Download necessary NLTK data if required
nltk.download('stopwords')
nltk.download('wordnet')

# 1. Load Your CSV Dataset
def load_data(csv_file):
    df = pd.read_csv(csv_file)
    return df

# 2. Handle Rare Classes
def filter_rare_classes(df, threshold=5):
    initial_classes = df['category_combined'].nunique()
    df_filtered = df.groupby('category_combined').filter(lambda x: len(x) >= threshold)
    final_classes = df_filtered['category_combined'].nunique()
    print(f"Removed {initial_classes - final_classes} rare classes with less than {threshold} samples.")
    return df_filtered

# 3. Data Cleaning and Preprocessing
def preprocess_text(text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    text = str(text)  # Convert to string to handle NaNs or other non-string types
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    text = text.strip()
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    cleaned_text = ' '.join(tokens)
    return cleaned_text

def preprocess_dataframe(df):
    # Handle missing or NaN values in 'headline' column by filling with empty strings
    df['headline'].fillna('', inplace=True)
    
    # Apply text preprocessing to 'headline' only
    df['headline_clean'] = df['headline'].apply(preprocess_text)
    return df

# 4. Feature Extraction with TF-IDF Vectorization
def extract_features(df, max_features=20000, ngram_range=(1, 3), min_df=5, max_df=0.7):
    tfidf = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        stop_words='english',
        min_df=min_df,
        max_df=max_df
    )
    X = tfidf.fit_transform(df['headline_clean'])
    return X, tfidf

# 5. Label Encoding
def encode_labels(df):
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df['category_combined'])
    category_mapping = dict(zip(label_encoder.classes_, range(len(label_encoder.classes_))))
    print("\nCategory-to-Number Mapping:")
    for category, number in category_mapping.items():
        print(f"{number} --> {category}")
    return y, label_encoder

# 6. Handle Class Imbalance
def compute_class_weights(y, classes):
    weights = class_weight.compute_class_weight('balanced', classes=classes, y=y)
    class_weights = dict(zip(classes, weights))
    print("\nClass Weights:", class_weights)
    return class_weights

# 7. Train-Test Split
def split_data(X, y, test_size=0.2, random_state=42):
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)

# 8. Define Logistic Regression Model
def define_model():
    model = LogisticRegression(max_iter=1000, class_weight='balanced')
    return model

# 9. Train and Evaluate Logistic Regression Model
def evaluate_model(model, X_train, y_train, X_test, y_test, label_encoder):
    print("\nTraining and evaluating Logistic Regression...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    unique_classes = np.unique(np.concatenate((y_test, y_pred)))
    print("Classification Report:\n", classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        labels=unique_classes
    ))
    print("Accuracy:", accuracy_score(y_test, y_pred))
    return model

# 10. Save Model, TF-IDF, and Label Encoder
def save_model_objects(model, tfidf, label_encoder):
    joblib.dump(model, 'best_model.pkl')
    joblib.dump(tfidf, 'tfidf_vectorizer.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl')
    print("Model, TF-IDF vectorizer, and label encoder saved.")

# Main Function to Execute All Steps
def main():
    # Load the CSV file
    csv_file = r"D:\NLP\NewspaperScrape\NewspaperScrape\combined_news_categories.csv"
    df = load_data(csv_file)
    
    # Handle rare classes by removing categories with less than 5 samples
    df = filter_rare_classes(df, threshold=5)
    class_counts = df['category_combined'].value_counts()
    print("\nPost-Filtering Class Distribution:\n", class_counts)

    # Preprocess the dataframe
    df = preprocess_dataframe(df)
    
    # Extract features using TF-IDF vectorizer
    X, tfidf = extract_features(df)
    
    # Encode the category_combined labels
    y, label_encoder = encode_labels(df)
    
    # Handle class imbalance
    classes = np.unique(y)
    class_weights = compute_class_weights(y, classes)

    # Split the data into train and test sets
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Define and train Logistic Regression model
    model = define_model()
    best_model = evaluate_model(model, X_train, y_train, X_test, y_test, label_encoder)

    # Save the model, vectorizer, and label encoder
    save_model_objects(best_model, tfidf, label_encoder)

if __name__ == "__main__":
    main()
