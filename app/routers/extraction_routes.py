from fastapi import APIRouter, HTTPException, Request, Depends
from app.functions.base import ImageRequest, ProductVerificationRequest, URLRequest
from app.services.openai_parser import parse_images_with_openai, parse_inner_text_with_openai
from app.services.clip_verifier import verify_image_with_clip
from app.services.vision_verifier import verify_with_openai_vision
from app.services.bert_verifier import predict_product_page
from app.utils.utils import extract_product_name_from_url
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.config.settings import settings
from app.utils.rate_limiter import rate_limit

router = APIRouter()

# Default image if verification fails
DEFAULT_IMAGE_URL = "https://example.com/default.jpg"

@router.post("/verify-image")
@rate_limit("10/minute")
async def verify_product(
    request: Request,
    payload: ProductVerificationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Verify if the extracted image matches the product name before storing the item.
    
    Uses a hybrid approach:
    1. First tries CLIP (fast, free)
    2. If CLIP fails and fallback is enabled, tries OpenAI Vision (more accurate, costs money)
    """
    try:
        if not payload.product_name or not str(payload.image_url).strip():
            raise HTTPException(status_code=400, detail="Missing product name or image URL.")

        image_url_str = str(payload.image_url)
        print(f"Verifying Product: {payload.product_name} | Price: {payload.price} | Image: {image_url_str}")

        # Step 1: Try CLIP verification (fast, free)
        is_valid_image = await verify_image_with_clip(image_url_str, payload.product_name)
        
        # Step 2: If CLIP fails and fallback is enabled, try OpenAI Vision
        if not is_valid_image and settings.ENABLE_VISION_FALLBACK:
            print(f"CLIP verification failed, trying OpenAI Vision fallback...")
            is_valid_image = await verify_with_openai_vision(image_url_str, payload.product_name)

        # Return the original image if valid, otherwise return the default image
        final_image_url = image_url_str if is_valid_image else DEFAULT_IMAGE_URL

        return {
            "product_name": payload.product_name,
            "price": payload.price,
            "verified_image_url": final_image_url
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@router.post("/analyze-images")
@rate_limit("10/minute")
async def analyze_images(
    request: Request,
    payload: ImageRequest,
    current_user: User = Depends(get_current_user)
):
    """Endpoint to analyze and determine the best product image."""
    try:
        if not payload.page_url or not payload.image_urls.strip():
            raise HTTPException(status_code=400, detail="Missing page_url or image_urls.")

        # Extract product name from page URL
        page_url_str = str(payload.page_url)
        product_name = extract_product_name_from_url(page_url_str)

        print(product_name)

        # Convert comma-separated URLs to a list
        image_urls = [url.strip() for url in payload.image_urls.split(",") if url.strip()]

        if not image_urls:
            raise HTTPException(status_code=400, detail="No valid image URLs found.")
        
        #FILTERING
        #filtered_image_urls = filter_images(product_name=product_name,image_urls=image_urls)

        # Call OpenAI function
        result = parse_images_with_openai(page_url_str, product_name, image_urls)
        
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/extract")
@rate_limit("10/minute")
async def extract_cart_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    try:
        # Receive plain text input
        input_text = await request.body()
        input_text = input_text.decode("utf-8").strip()

        if not input_text:
            raise HTTPException(status_code=400, detail="Invalid input: Expecting plain text input.")

        # Call the parser
        extracted_data = parse_inner_text_with_openai(input_text)

        return {"cart_items": extracted_data}

    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@router.post("/classify-url")
@rate_limit("10/minute")
async def classify_url(
    request: Request,
    url_request: URLRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Receives a URL, runs BERT classification, and returns whether it is a product page (1) or not (0).
    """
    try:
        url_str = str(url_request.url)
        prediction = predict_product_page(url_str)
        return {"url": url_str, "is_product_page": bool(prediction)}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=503,
            detail=f"BERT model not available: {str(e)}. Please configure BERT_MODEL_PATH in your .env file."
        )