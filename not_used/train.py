import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os

# Paths
DATA_PATH = "data/training_data/processed/"
MODEL_PATH = "data/model/model.pkl"

# Load Data
def load_training_data():
    features, labels = [], []
    for file in os.listdir(DATA_PATH):
        if file.endswith(".npz"):
            data = np.load(os.path.join(DATA_PATH, file), allow_pickle=True)
            features.append(data["features"])
            labels.append(data["labels"])
    return np.vstack(features), np.hstack(labels)

# Train Model
def train_model():
    features, labels = load_training_data()
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    # Save Model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

if __name__ == "__main__":
    train_model()
