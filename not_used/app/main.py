from fastapi import FastAPI, HTTPException, Request
from app.ml_model import predict_from_html
from app.utils import preprocess_html

app = FastAPI()

@app.post("/extract")
async def extract_cart_info(request: Request):
    try:
        # Parse HTML from the request
        data = await request.json()
        html_content = data.get("html")
        if not html_content:
            raise HTTPException(status_code=400, detail="No HTML content provided.")

        # Preprocess HTML
        features = preprocess_html(html_content)

        # Predict using the ML model
        predictions = predict_from_html(features)

        return {"cart_items": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))