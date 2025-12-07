import torch
import open_clip
from PIL import Image
import httpx
from io import BytesIO
from app.config.settings import settings

# Lazy loading: Model components loaded on first use
_model = None
_tokenizer = None
_preprocess_val = None
_device = None
_model_loading = False  # Flag to prevent concurrent loading

def _load_model():
    """Lazy load the CLIP model and tokenizer on first use."""
    global _model, _tokenizer, _preprocess_val, _device, _model_loading
    
    if _model is None and not _model_loading:
        _model_loading = True
        try:
            _device = "cuda" if torch.cuda.is_available() else "cpu"
            # Use ViT-B-32-quickgelu variant to match OpenAI pretrained model (fixes QuickGELU warning)
            _model, _, _preprocess_val = open_clip.create_model_and_transforms(
                'ViT-B-32-quickgelu', 
                pretrained='openai'
            )
            # Move the model to the appropriate device
            _model.to(_device)
            _model.eval()  # Set to evaluation mode
            _tokenizer = open_clip.get_tokenizer('ViT-B-32-quickgelu')
        finally:
            _model_loading = False
    
    return _model, _tokenizer, _preprocess_val, _device

async def verify_image_with_clip(image_url: str, product_name: str) -> bool:
    """
    Verify if an image matches a product name using CLIP model.
    
    Args:
        image_url: URL of the image to verify
        product_name: Name of the product to match against
        
    Returns:
        True if image matches product name (similarity >= threshold), False otherwise
    """
    try:
        # Lazy load model (synchronous operation, but called from async context)
        model, tokenizer, preprocess_val, device = _load_model()
        
        # Tokenize the product name
        text_tokens = tokenizer([product_name])

        # Download and preprocess the image (async HTTP)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()
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

        # Use configurable threshold from settings (default 0.28)
        threshold = settings.CLIP_THRESHOLD
        return similarity >= threshold

    except httpx.HTTPError as e:
        print(f"HTTP error verifying image with CLIP: {e}")
        return False
    except Exception as e:
        print(f"Error verifying image with CLIP: {e}")
        return False

def check_clip_model_status() -> dict:
    """Check if CLIP model is available (loaded or loadable)."""
    try:
        _load_model()
        return {"status": "ok", "loaded": _model is not None}
    except Exception as e:
        return {"status": "error", "message": str(e)}