"""Feedback repository for database operations."""
from typing import Dict, Any
from app.repositories.base import BaseRepository
from app.core.database import feedback_collection


class FeedbackRepository(BaseRepository):
    """Repository for feedback database operations."""
    
    def __init__(self):
        super().__init__(feedback_collection)
    
    async def create(self, feedback_data: Dict[str, Any]) -> str:
        """
        Create a new feedback entry.
        
        Args:
            feedback_data: Feedback document dictionary
            
        Returns:
            Feedback ID
        """
        await self.insert_one(feedback_data)
        return feedback_data.get("feedback_id")

