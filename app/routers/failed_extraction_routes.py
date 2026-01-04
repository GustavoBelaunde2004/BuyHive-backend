from fastapi import APIRouter, HTTPException, Request, Depends
from app.schemas.failed_extraction import FailedExtractionRequest
from app.services.failed_extraction_service import FailedExtractionService
from app.core.dependencies import get_failed_extraction_service, get_current_user
from app.models.user import User
from app.utils.rate_limiter import rate_limit

router = APIRouter()

@router.post("/submit", response_model=dict)
@rate_limit("20/minute")
async def submit_failed_extraction(
    request: Request,
    payload: FailedExtractionRequest,
    current_user: User = Depends(get_current_user),
    extraction_service: FailedExtractionService = Depends(get_failed_extraction_service)
):
    """
    Submit failed extraction (record URL that failed frontend extraction).
    Saves to MongoDB for analytics and identifying unsupported websites.
    """
    try:
        result = await extraction_service.submit_failed_extraction(
            url=str(payload.url),
            user_id=current_user.user_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing failed extraction: {str(e)}"
        )

