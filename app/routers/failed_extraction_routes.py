from fastapi import APIRouter, HTTPException, Request, Depends
from app.schemas.failed_extraction import FailedPageExtractionRequest, FailedItemExtractionRequest
from app.services.failed_extraction_service import FailedExtractionService
from app.core.dependencies import get_failed_extraction_service
from app.utils.rate_limiter import rate_limit

router = APIRouter()

@router.post("/page", response_model=dict)
@rate_limit("20/minute")
async def submit_failed_page_extraction(
    request: Request,
    payload: FailedPageExtractionRequest,
    extraction_service: FailedExtractionService = Depends(get_failed_extraction_service)
):
    """
    Submit failed page extraction (record URL that failed page extraction).
    Saves to MongoDB for analytics and identifying unsupported websites.
    """
    try:
        result = await extraction_service.submit_failed_page_extraction(
            url=str(payload.url),
            failure_type=payload.failure_type,
            confidence=payload.confidence
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing failed page extraction: {str(e)}"
        )


@router.post("/item", response_model=dict)
@rate_limit("20/minute")
async def submit_failed_item_extraction(
    request: Request,
    payload: FailedItemExtractionRequest,
    extraction_service: FailedExtractionService = Depends(get_failed_extraction_service)
):
    """
    Submit failed item extraction (record item that had low confidence extraction).
    Saves to MongoDB for analytics and quality review.
    """
    try:
        result = await extraction_service.submit_failed_item_extraction(
            url=str(payload.url),
            type=payload.type,
            image_confidence=payload.image_confidence,
            name_confidence=payload.name_confidence,
            price_confidence=payload.price_confidence
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing failed item extraction: {str(e)}"
        )

