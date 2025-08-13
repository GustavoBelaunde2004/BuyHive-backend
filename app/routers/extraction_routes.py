from fastapi import APIRouter, HTTPException, Request
from app.functions.base import ImageRequest, ProductVerificationRequest, URLRequest
from app.services.openai_parser import parse_images_with_openai,parse_inner_text_with_openai
from app.services.clip_verifier import verify_image_with_clip
from app.services.bert_verifier import predict_product_page
from app.utils.utils import extract_product_name_from_url

router = APIRouter()

# Default image if CLIP verification fails
DEFAULT_IMAGE_URL = "https://example.com/default.jpg"

@router.post("/verify-image")
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
    
@router.post("/analyze-images")
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

@router.post("/extract")
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
    
@router.post("/classify-url")
async def classify_url(request: URLRequest):
    """
    Receives a URL, runs BERT classification, and returns whether it is a product page (1) or not (0).
    """
    prediction = predict_product_page(request.url)
    return {"url": request.url, "is_product_page": bool(prediction)}