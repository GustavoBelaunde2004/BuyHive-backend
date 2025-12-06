import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from app.config.settings import settings
import os

# Load Model and Tokenizer
MODEL_PATH = settings.BERT_MODEL_PATH
MODEL_AVAILABLE = False

# Check if model path is provided and exists
if MODEL_PATH and os.path.exists(MODEL_PATH):
    MODEL_AVAILABLE = True
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = None
    tokenizer = None
else:
    # Model not available - will fail gracefully when called
    MODEL_AVAILABLE = False
    model = None
    tokenizer = None
    device = None

def _load_model():
    """Lazy load the BERT model and tokenizer."""
    global model, tokenizer, MODEL_AVAILABLE
    
    if not MODEL_AVAILABLE:
        raise ValueError("BERT model is not available. Please set BERT_MODEL_PATH in .env file and ensure the path exists.")
    
    if model is None or tokenizer is None:
        model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH).to(device)
        tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
    return model, tokenizer

def predict_product_page(url, threshold=0.85):  # Threshold to reduce false positives
    """
    Predicts whether a given URL is a product page (1) or not (0).
    Uses a confidence threshold to prevent misclassification.
    """
    if not MODEL_AVAILABLE:
        raise ValueError("BERT model is not available. Please set BERT_MODEL_PATH in .env file and ensure the path exists.")
    
    # Lazy load model if not already loaded
    model, tokenizer = _load_model()
    
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
