import joblib
from model import preprocess_text  # Assuming the preprocess function is in the same module

# Load the trained model, TF-IDF vectorizer, and label encoder
best_model = joblib.load('best_model.pkl')
tfidf = joblib.load('tfidf_vectorizer.pkl')
label_encoder = joblib.load('label_encoder.pkl')

# Define the predict_category function
def predict_category(new_headline):
    # Preprocess the new headline
    new_cleaned_text = preprocess_text(new_headline)
    
    # Transform the headline using the trained TF-IDF vectorizer
    new_tfidf = tfidf.transform([new_cleaned_text])

    # Predict the category for the new headline
    predicted_category = best_model.predict(new_tfidf)
    
    # Get the predicted category label
    predicted_category_label = label_encoder.inverse_transform(predicted_category)
    
    return predicted_category_label[0]

# Example usage
headline = "New tech innovations announced at conference"
predicted_category = predict_category(headline)
print(f"Predicted Category: {predicted_category}")
