from fastapi import APIRouter, HTTPException, Request
from app.schemas.feedback import FeedbackFormRequest
from app.services.feedback_service import FeedbackService
from app.core.dependencies import get_feedback_service
from fastapi import Depends
from app.utils.rate_limiter import rate_limit

router = APIRouter()

@router.post("/submit", response_model=dict)
@rate_limit("10/minute")
async def submit_feedback(
    request: Request,
    payload: FeedbackFormRequest,
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """
    Submit feedback (bug report or feature request).
    Saves to MongoDB and posts to Google Sheets.
    """
    try:
        result = await feedback_service.submit_feedback(
            type=payload.type,
            description=payload.description,
            firstName=payload.firstName,
            lastName=payload.lastName,
            email=payload.email,
            timestamp=payload.timestamp
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing feedback: {str(e)}"
        )
