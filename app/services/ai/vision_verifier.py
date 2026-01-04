"""
OpenAI Vision API verifier for image verification.
Used as a fallback when CLIP verification fails.
"""
from openai import OpenAI
from app.core.config import settings
import httpx

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

async def verify_with_openai_vision(image_url: str, product_name: str) -> bool:
    """
    Verify if an image matches a product name using OpenAI Vision API.
    
    This is more accurate than CLIP but costs money per request.
    Used as a fallback when CLIP verification fails.
    
    Args:
        image_url: URL of the image to verify
        product_name: Name of the product to match against
        
    Returns:
        True if image matches product name, False otherwise
    """
    if not client:
        return False
    
    try:
        # Create a prompt for OpenAI Vision
        prompt = f"""Does this image show a product called "{product_name}"?
        
        Respond with only "yes" or "no". Consider:
        - The image should clearly show the product described by the name
        - The product in the image should match the name (not a different product)
        - Generic placeholder images or unrelated images should return "no"
        """
        
        # Call OpenAI Vision API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=10,
            temperature=0,
        )
        
        # Parse response
        result = response.choices[0].message.content.strip().lower()
        return result.startswith("yes")
        
    except Exception as e:
        print(f"Error verifying image with OpenAI Vision: {e}")
        return False

async def check_openai_vision_availability() -> dict:
    """Check if OpenAI Vision API is available."""
    if not client:
        return {"status": "unavailable", "message": "OpenAI API key not configured"}
    
    try:
        # Simple test to verify API is working
        # We don't actually make a call, just check if client is configured
        return {"status": "ok", "configured": True}
    except Exception as e:
        return {"status": "error", "message": str(e)}

