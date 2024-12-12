from fastapi import FastAPI, HTTPException, Request
from app.openai_parser import parse_html_with_openai

app = FastAPI()

@app.post("/extract")
async def extract_cart_info(request: Request):
    try:
        # Parse HTML from the request
        data = await request.json()
        html_content = data.get("html")
        if not html_content:
            raise HTTPException(status_code=400, detail="No HTML content provided.")

        # Use OpenAI to parse HTML and extract information
        extracted_data = parse_html_with_openai(html_content)

        return {"cart_items": extracted_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))