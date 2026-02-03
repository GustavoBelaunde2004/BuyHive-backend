from pydantic import BaseModel
from typing import Dict, Any, Optional


class Feedback(BaseModel):
    """Database representation of a Feedback submission."""
    feedback_id: str  # UUID
    type: str
    description: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    timestamp: str  # ISO datetime string
    created_at: str  # ISO datetime string
    
    @classmethod
    def from_mongo(cls, doc: Dict[str, Any]) -> "Feedback":
        """
        Convert MongoDB document to Feedback model.
        
        Args:
            doc: MongoDB document dictionary
            
        Returns:
            Feedback instance
        """
        return cls(**doc)
    
    def to_mongo_dict(self) -> Dict[str, Any]:
        """
        Convert Feedback model to MongoDB document dict.
        
        Returns:
            Dictionary suitable for MongoDB storage
        """
        return self.model_dump(exclude_none=False)

