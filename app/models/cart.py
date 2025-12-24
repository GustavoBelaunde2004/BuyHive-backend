from pydantic import BaseModel
from typing import List, Dict, Any


class Cart(BaseModel):
    """Database representation of a Cart."""
    cart_id: str  # UUID
    cart_name: str
    item_count: int = 0
    created_at: str  # ISO datetime string
    item_ids: List[str] = []
    
    @classmethod
    def from_mongo(cls, doc: Dict[str, Any]) -> "Cart":
        """
        Convert MongoDB document to Cart model.
        
        Args:
            doc: MongoDB document dictionary
            
        Returns:
            Cart instance
        """
        doc_copy = doc.copy()
        return cls(**doc_copy)
    
    def to_mongo_dict(self) -> Dict[str, Any]:
        """
        Convert Cart model to MongoDB document dict.
        
        Returns:
            Dictionary suitable for MongoDB storage
        """
        return self.model_dump(exclude_none=False)

