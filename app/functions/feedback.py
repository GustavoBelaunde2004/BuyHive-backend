from datetime import datetime
from uuid import uuid4
from typing import Dict
from .database import feedback_collection
from app.models.feedback import Feedback
from app.config.settings import settings
import httpx


async def save_feedback(
    type: str,
    description: str,
    firstName: str,
    lastName: str,
    email: str,
    timestamp: str
) -> Dict:
    """
    Save feedback to MongoDB and post to Google Sheets.
    
    Args:
        type: Type of feedback (e.g., "bug", "feature_request")
        description: Description of the feedback
        firstName: User's first name
        lastName: User's last name
        email: User's email address
        timestamp: ISO format timestamp from the client
    
    Returns:
        dict with success message and feedback_id
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
    await feedback_collection.insert_one(feedback_doc)
    
    # Post to Google Sheets
    try:
        if settings.GOOGLE_SHEETS_SCRIPT_URL:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Google Apps Script expects URLSearchParams (form data)
                form_data = {
                    "type": type,
                    "description": description,
                    "firstName": firstName,
                    "lastName": lastName,
                    "email": email,
                    "timestamp": timestamp
                }
                
                response = await client.post(
                    settings.GOOGLE_SHEETS_SCRIPT_URL,
                    data=form_data,  # This sends as application/x-www-form-urlencoded
                    follow_redirects=True  # Google Apps Script may redirect
                )
                response.raise_for_status()
        else:
            print("Warning: GOOGLE_SHEETS_SCRIPT_URL not configured, skipping Google Sheets post")
            
    except httpx.HTTPError as e:
        # Log error but don't fail the request if MongoDB save succeeded
        print(f"Warning: Failed to post to Google Sheets: {str(e)}")
        # You might want to log this to a monitoring service
    
    return {
        "message": "Feedback submitted successfully",
        "feedback_id": feedback_id
    }

