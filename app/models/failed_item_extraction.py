from pydantic import BaseModel
from typing import Dict, Any


class FailedItemExtraction(BaseModel):
    """Database representation of a Failed Item Extraction entry."""
    extraction_id: str  # UUID
    url: str
    domain: str  # Extracted domain (e.g., "amazon.com")
    type: str  # Type of failure (e.g., "maybe", "not_a_product")
    image_confidence: float  # Confidence for image extraction (0.0-1.0)
    name_confidence: float  # Confidence for name extraction (0.0-1.0)
    price_confidence: float  # Confidence for price extraction (0.0-1.0)
    timestamp: str  # ISO datetime string (server-generated)
    created_at: str  # ISO datetime string
    
    @classmethod
    def from_mongo(cls, doc: Dict[str, Any]) -> "FailedItemExtraction":
        """
        Convert MongoDB document to FailedItemExtraction model.
        
        Args:
            doc: MongoDB document dictionary
            
        Returns:
            FailedItemExtraction instance
        """
        return cls(**doc)
    
    def to_mongo_dict(self) -> Dict[str, Any]:
        """
        Convert FailedItemExtraction model to MongoDB document dict.
        
        Returns:
            Dictionary suitable for MongoDB storage
        """
        return self.model_dump(exclude_none=False)

