from pydantic import BaseModel
from typing import Dict, Any


class FailedExtraction(BaseModel):
    """Database representation of a Failed Extraction entry."""
    extraction_id: str  # UUID
    url: str
    domain: str  # Extracted domain (e.g., "amazon.com")
    user_id: str
    timestamp: str  # ISO datetime string (server-generated)
    created_at: str  # ISO datetime string
    
    @classmethod
    def from_mongo(cls, doc: Dict[str, Any]) -> "FailedExtraction":
        """
        Convert MongoDB document to FailedExtraction model.
        
        Args:
            doc: MongoDB document dictionary
            
        Returns:
            FailedExtraction instance
        """
        return cls(**doc)
    
    def to_mongo_dict(self) -> Dict[str, Any]:
        """
        Convert FailedExtraction model to MongoDB document dict.
        
        Returns:
            Dictionary suitable for MongoDB storage
        """
        return self.model_dump(exclude_none=False)

