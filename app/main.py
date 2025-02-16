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
    image_urls: List[str]

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
async def analyze_images(payload: Request):
    """Endpoint to analyze and determine the best product image."""
    try:
        # Read and decode the request body as plain text
        input_text = await payload.body()
        input_text = input_text.decode("utf-8").strip()

        if not input_text:
            raise HTTPException(status_code=400, detail="Invalid input: Expecting plain text containing image URLs.")

        # Split the input text into URLs (split on whitespace, commas, or newlines)
        image_urls = [url.strip() for url in input_text.split() if url.strip()]

        if not image_urls:
            raise HTTPException(status_code=400, detail="No valid image URLs found in the input.")

        # Call the parser function
        result = parse_images_with_openai(image_urls)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
