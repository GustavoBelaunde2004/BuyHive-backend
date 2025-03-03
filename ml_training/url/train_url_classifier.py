import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import pickle

# Load dataset
df = pd.read_csv("C:\GUSTAVO\Projects\Extension\Extension-backend\ecommerce_urls.csv")

# Drop blank rows
df = df.dropna()

# Extract features and labels
X = df["url"].astype(str) 
y = df["label"].astype(int)

# Text vectorization
vectorizer = TfidfVectorizer(ngram_range=(1,2), stop_words="english")
X_vectorized = vectorizer.fit_transform(X)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

# Train Logistic Regression Model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 🔹 Evaluate Model Performance
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {accuracy * 100:.2f}%")

print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))

# Save vectorizer and model correctly
with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("url_classifier.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model and vectorizer saved successfully!")