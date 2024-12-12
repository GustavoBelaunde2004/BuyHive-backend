from bs4 import BeautifulSoup
import json
import numpy as np
import os

RAW_DATA_PATH = "data/training_data/raw/"
PROCESSED_DATA_PATH = "data/training_data/processed/"

def extract_features_and_labels(html_file):
    """
    Extract features from an HTML file and assign labels manually.
    :param html_file: Path to the raw HTML file.
    """
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    elements = soup.find_all()
    features = []
    labels = []

    # Attempt to extract JSON-LD structured data
    json_ld_data = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            json_ld_data.append(json.loads(script.string))
        except (TypeError, json.JSONDecodeError):
            continue

    for element in elements:
        feature = {
            "tag": element.name,
            "attributes": " ".join([f"{k}={v}" for k, v in element.attrs.items()]),
            "text_length": len(element.text.strip()),
            "position": elements.index(element)  # Position in the DOM
        }
        features.append(feature)

        # Placeholder for manual labeling (replace with actual logic or tool)
        labels.append("other")  # Default label

    return {"features": features, "json_ld": json_ld_data}, labels

def process_all_files():
    all_features = []
    all_labels = []

    for file in os.listdir(RAW_DATA_PATH):
        if file.endswith(".html"):
            data, labels = extract_features_and_labels(os.path.join(RAW_DATA_PATH, file))
            all_features.extend(data["features"])
            all_labels.extend(labels)

    # Convert to arrays and save
    np.savez(os.path.join(PROCESSED_DATA_PATH, "training_data.npz"),
             features=all_features, labels=all_labels)

if __name__ == "__main__":
    process_all_files()