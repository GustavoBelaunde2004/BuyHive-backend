import pickle
import numpy as np

MODEL_PATH = "data/model/model.pkl"

# Load the ML model (placeholder for now)
def load_model():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    return model

model = load_model()

# Predict from processed features
def predict_from_html(features: list):
    predictions = model.predict(features)
    return predictions