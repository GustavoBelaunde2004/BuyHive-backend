from fastapi import FastAPI, HTTPException, Request
from app.openai_parser import parse_html_with_openai

app = FastAPI()

@app.post("/extract")
async def extract_cart_info(request: Request):
    try:
        # Parse JSON body
        data = await request.json()
        html_content = data.get("html")
        if not html_content:
            raise HTTPException(status_code=400, detail="No HTML content provided.")

        # Call the OpenAI parser
        extracted_data = parse_html_with_openai(html_content)

        return {"cart_items": extracted_data}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
