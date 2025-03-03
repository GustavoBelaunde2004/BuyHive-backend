import pickle
import re
import sys
import pickle

try:
    with open(r"vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    print("Successfully loaded vectorizer.")

    with open(r"url_classifier.pkl", "rb") as g:
        model = pickle.load(g)
    print("Successfully loaded model.")

except pickle.UnpicklingError as e:
    print("Corrupted file:", e)
except FileNotFoundError:
    print("File not found. Check your file path.")


def clean_url(url):
    """Preprocess URL: Remove tracking parameters, session IDs, etc."""
    url = re.sub(r"https?://(www\.)?", "", url)
    url = re.sub(r"(\?|#).*", "", url)
    url = re.sub(r"/$", "", url)
    return url

def predict_url(url):
    """Predict if a URL is an item product page (1) or not (0)."""
    cleaned_url = url #IM NOT USING CLEAN_URL FUNCTION
    url_vectorized = vectorizer.transform([cleaned_url])
    prediction = model.predict(url_vectorized)[0]
    return prediction

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict_url.py <URL>")
        sys.exit(1)
    
    url_to_test = sys.argv[1]
    result = predict_url(url_to_test)
    print(f"🔹 URL: {url_to_test}")
    print(f"✅ Prediction: {'Product Page' if result == 1 else 'Not a Product Page'}")
