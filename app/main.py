from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.openai_parser import parse_images_with_openai,parse_inner_text_with_openai
from app.routes import router as cart_router
from pydantic import BaseModel
import torch
import open_clip
from PIL import Image
import requests
from io import BytesIO

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageRequest(BaseModel):
    page_url: str
    image_urls: str

# Default image if CLIP verification fails
DEFAULT_IMAGE_URL = "https://example.com/default.jpg"

class ProductVerificationRequest(BaseModel):
    product_name: str
    price: str
    image_url: str

# Determine the device to run the model on
device = "cuda" if torch.cuda.is_available() else "cpu"
# Load the model and preprocessing transforms
model, preprocess_train, preprocess_val = open_clip.create_model_and_transforms(
    'ViT-B-32', pretrained='openai'
)
# Move the model to the appropriate device
model.to(device)
tokenizer = open_clip.get_tokenizer('ViT-B-32')

# Register routes
app.include_router(cart_router)

@app.post("/extract")
async def extract_cart_info(request: Request):
    try:
        # Receive plain text input
        input_text = await request.body()
        input_text = input_text.decode("utf-8").strip()

        if not input_text:
            raise HTTPException(status_code=400, detail="Invalid input: Expecting plain text input.")

        # Call the parser
        extracted_data = parse_inner_text_with_openai(input_text)

        return {"cart_items": extracted_data}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@app.post("/analyze-images")
async def analyze_images(payload: ImageRequest):
    """Endpoint to analyze and determine the best product image."""
    try:
        if not payload.page_url or not payload.image_urls.strip():
            raise HTTPException(status_code=400, detail="Missing page_url or image_urls.")

        # Extract product name from page URL
        product_name = extract_product_name_from_url(payload.page_url)

        print(product_name)

        # Convert comma-separated URLs to a list
        image_urls = [url.strip() for url in payload.image_urls.split(",") if url.strip()]

        if not image_urls:
            raise HTTPException(status_code=400, detail="No valid image URLs found.")
        
        #FILTERING
        #filtered_image_urls = filter_images(product_name=product_name,image_urls=image_urls)

        # Call OpenAI function
        result = parse_images_with_openai(payload.page_url, product_name, image_urls)
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

def extract_product_name_from_url(url: str) -> str:
    """Extracts the product name from a URL by removing domain and numeric IDs."""
    from urllib.parse import urlparse

    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split("/")  # Extract path sections

    # Remove numeric segments (likely product IDs)
    words = [part for part in path_parts if not part.isdigit() and len(part) > 2]

    # Join cleaned segments
    product_name = " ".join(words).replace("-", " ").replace("_", " ").strip()
    #print(product_name)

    return product_name if product_name else "Unknown Product"

@app.post("/verify-image")
async def verify_product(payload: ProductVerificationRequest):
    """Verify if the extracted image matches the product name before storing the item."""
    try:
        if not payload.product_name or not payload.image_url.strip():
            raise HTTPException(status_code=400, detail="Missing product name or image URL.")

        print(f"Verifying Product: {payload.product_name} | Price: {payload.price} | Image: {payload.image_url}")

        # Run CLIP verification
        is_valid_image = verify_image_with_clip(payload.image_url, payload.product_name)

        # Return the original image if valid, otherwise return the default image
        final_image_url = payload.image_url if is_valid_image else DEFAULT_IMAGE_URL

        return {
            "product_name": payload.product_name,
            "price": payload.price,
            "verified_image_url": final_image_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

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