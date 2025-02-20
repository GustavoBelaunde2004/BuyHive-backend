from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.openai_parser import parse_images_with_openai,parse_inner_text_with_openai
from app.routes import router as cart_router
from pydantic import BaseModel
from typing import List

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

def filter_images(image_urls: list, product_name: str) -> list:
    """Filters out irrelevant images while keeping relevant ones for any shopping website."""
    filtered_urls = []
    product_name_lower = product_name.lower()

    for url in image_urls:
        url_lower = url.lower()

        # Exclude bad keywords
        if any(bad_word in url_lower for bad_word in ["thumbnail", "icon", "logo", "banner", "ads", "promo"]):
            continue

        # Exclude SVGs (usually UI elements, not real product images)
        if url_lower.endswith(".svg"):
            continue

        # Keep URLs that contain the product name (best indicator)
        if product_name_lower in url_lower:
            filtered_urls.insert(0, url)

        # Prioritize URLs that include common product image markers
        elif any(keyword in url_lower for keyword in ["product", "main", "large", "featured", "media"]):
            filtered_urls.append(url)

        # Only keep URLs with valid image extensions
        #elif url_lower.endswith((".jpeg", ".jpg", ".png")):
        #    filtered_urls.append(url)
        print(filtered_urls)

    return filtered_urls
