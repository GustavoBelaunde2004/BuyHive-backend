from fastapi import APIRouter, HTTPException, Request, Depends
from app.schemas.extraction import ImageRequest, InnerTextRequest
from app.services.ai.openai_parser import parse_images_with_openai, parse_inner_text_with_openai
from app.utils.utils import extract_product_name_from_url
from app.core.dependencies import get_current_user
from app.models.user import User
from app.utils.rate_limiter import rate_limit

router = APIRouter()

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
    payload: InnerTextRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        # Call the parser
        extracted_data = parse_inner_text_with_openai(payload.inner_text)

        return {"cart_items": extracted_data}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")