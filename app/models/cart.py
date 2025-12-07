from pydantic import BaseModel
from typing import List, Dict, Any
from app.models.item import ItemInDB


class Cart(BaseModel):
    """Database representation of a Cart."""
    cart_id: str  # UUID
    cart_name: str
    item_count: int = 0
    created_at: str  # ISO datetime string
    items: List[ItemInDB] = []
    
    @classmethod
    def from_mongo(cls, doc: Dict[str, Any]) -> "Cart":
        """
        Convert MongoDB document to Cart model.
        
        Args:
            doc: MongoDB document dictionary
            
        Returns:
            Cart instance
        """
        # Convert items list to ItemInDB objects
        items = []
        for item_doc in doc.get("items", []):
            items.append(ItemInDB.from_mongo(item_doc))
        
        doc_copy = doc.copy()
        doc_copy["items"] = items
        return cls(**doc_copy)
    
    def to_mongo_dict(self) -> Dict[str, Any]:
        """
        Convert Cart model to MongoDB document dict.
        
        Returns:
            Dictionary suitable for MongoDB storage
        """
        result = self.model_dump(exclude_none=False)
        # Convert ItemInDB objects to dicts
        result["items"] = [item.to_mongo_dict() for item in self.items]
        return result

