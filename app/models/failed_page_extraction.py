from pydantic import BaseModel
from typing import Dict, Any


class FailedPageExtraction(BaseModel):
    """Database representation of a Failed Page Extraction entry."""
    extraction_id: str  # UUID
    url: str
    domain: str  # Extracted domain (e.g., "amazon.com")
    failure_type: str  # Type of failure (e.g., "unsupported", "no_product", "parsing_error")
    confidence: float  # Confidence that this is a failure (0.0-1.0)
    timestamp: str  # ISO datetime string (server-generated)
    created_at: str  # ISO datetime string
    
    @classmethod
    def from_mongo(cls, doc: Dict[str, Any]) -> "FailedPageExtraction":
        """
        Convert MongoDB document to FailedPageExtraction model.
        
        Args:
            doc: MongoDB document dictionary
            
        Returns:
            FailedPageExtraction instance
        """
        return cls(**doc)
    
    def to_mongo_dict(self) -> Dict[str, Any]:
        """
        Convert FailedPageExtraction model to MongoDB document dict.
        
        Returns:
            Dictionary suitable for MongoDB storage
        """
        return self.model_dump(exclude_none=False)

