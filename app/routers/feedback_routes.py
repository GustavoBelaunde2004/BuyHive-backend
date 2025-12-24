from fastapi import APIRouter, HTTPException, Request
from app.functions.base import FeedbackFormRequest
from app.functions.feedback import save_feedback
from app.utils.rate_limiter import rate_limit

router = APIRouter()

@router.post("/submit")
@rate_limit("10/minute")
async def submit_feedback(
    request: Request,
    payload: FeedbackFormRequest
):
    """
    Submit feedback (bug report or feature request).
    Saves to MongoDB and posts to Google Sheets.
    """
    try:
        result = await save_feedback(
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

