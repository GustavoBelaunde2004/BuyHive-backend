"""Feedback service for business logic."""
from datetime import datetime
from uuid import uuid4
from typing import Dict, Optional
from app.repositories.feedback_repository import FeedbackRepository
from app.models.feedback import Feedback
from app.core.config import settings
import httpx


class FeedbackService:
    """Service for feedback business logic."""
    
    def __init__(self, feedback_repo: FeedbackRepository):
        """
        Initialize feedback service with repository.
        
        Args:
            feedback_repo: Feedback repository instance
        """
        self.feedback_repo = feedback_repo
    
    async def submit_feedback(
        self,
        type: str,
        description: str,
        timestamp: str,
        firstName: Optional[str] = None,
        lastName: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict:
        """
        Submit feedback (save to MongoDB and post to Google Sheets).
        
        Args:
            type: Type of feedback (e.g., "bug", "feature_request")
            description: Description of the feedback
            firstName: User's first name (optional)
            lastName: User's last name (optional)
            email: User's email address (optional)
            timestamp: ISO format timestamp from the client
            
        Returns:
            Dictionary with success message and feedback_id
        """
        feedback_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        
        # Create Feedback instance
        feedback = Feedback(
            feedback_id=feedback_id,
            type=type,
            description=description,
            firstName=firstName,
            lastName=lastName,
            email=email,
            timestamp=timestamp,
            created_at=now,
        )
        
        # Convert to MongoDB dict and save
        feedback_doc = feedback.to_mongo_dict()
        await self.feedback_repo.create(feedback_doc)
        
        # Post to Google Sheets (non-blocking)
        try:
            if settings.GOOGLE_SHEETS_SCRIPT_URL:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    form_data = {
                        "type": type,
                        "description": description,
                        "firstName": firstName or "",
                        "lastName": lastName or "",
                        "email": email or "",
                        "timestamp": timestamp
                    }
                    
                    response = await client.post(
                        settings.GOOGLE_SHEETS_SCRIPT_URL,
                        data=form_data,
                        follow_redirects=True
                    )
                    response.raise_for_status()
            else:
                print("Warning: GOOGLE_SHEETS_SCRIPT_URL not configured, skipping Google Sheets post")
                
        except httpx.HTTPError as e:
            # Log error but don't fail the request if MongoDB save succeeded
            print(f"Warning: Failed to post to Google Sheets: {str(e)}")
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id
        }

