import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# Load Model and Tokenizer
MODEL_PATH = r"C:\GUSTAVO\Projects\Extension\Extension-backend\ml_training\url\bert_models\bert_model_2"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH).to(device)
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)

def predict_product_page(url, threshold=0.85):  # Threshold to reduce false positives
    """
    Predicts whether a given URL is a product page (1) or not (0).
    Uses a confidence threshold to prevent misclassification.
    """
    # Tokenize the input URL
    inputs = tokenizer(url, truncation=True, padding="max_length", max_length=128, return_tensors="pt").to(device)

    with torch.no_grad():
        logits = model(**inputs).logits

    # Get probability scores
    probs = torch.nn.functional.softmax(logits, dim=-1)
    confidence, prediction = torch.max(probs, dim=-1)

    # Apply confidence threshold
    if confidence.item() < threshold:
        return 0  # Default to "Not a Product Page" if confidence is too low

    return prediction.item()
