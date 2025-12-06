import torch
import open_clip
from PIL import Image
import requests
from io import BytesIO

# Determine the device to run the model on
device = "cuda" if torch.cuda.is_available() else "cpu"
# Load the model and preprocessing transforms
# Use ViT-B-32-quickgelu variant to match OpenAI pretrained model (fixes QuickGELU warning)
model, preprocess_train, preprocess_val = open_clip.create_model_and_transforms(
    'ViT-B-32-quickgelu', 
    pretrained='openai'
)
# Move the model to the appropriate device
model.to(device)
tokenizer = open_clip.get_tokenizer('ViT-B-32-quickgelu')

def verify_image_with_clip(image_url: str, product_name: str) -> bool:
    try:
        # Tokenize the product name
        text_tokens = tokenizer([product_name])

        # Download and preprocess the image
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image_tensor = preprocess_val(image).unsqueeze(0).to(device)

        # Encode the image and text
        with torch.no_grad():
            image_features = model.encode_image(image_tensor)
            text_features = model.encode_text(text_tokens)

        # Normalize the features
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        # Compute the cosine similarity
        similarity = (image_features @ text_features.T).item()

        # Define a threshold for similarity
        threshold = 0.2
        return similarity >= threshold

    except Exception as e:
        print(f"Error verifying image with CLIP: {e}")
        return False