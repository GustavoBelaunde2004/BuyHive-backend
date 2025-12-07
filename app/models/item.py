from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from app.utils.sanitize import sanitize_product_name, sanitize_notes


class ItemInDB(BaseModel):
    """Database representation of an Item with all stored fields."""
    item_id: str  # UUID
    name: str
    price: str
    image: Optional[str] = None  # URL stored as string in MongoDB
    url: Optional[str] = None    # URL stored as string in MongoDB
    notes: Optional[str] = None
    added_at: str  # ISO datetime string
    selected_cart_ids: Optional[List[str]] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and sanitize item name."""
        if not v or not v.strip():
            raise ValueError("Item name cannot be empty")
        return sanitize_product_name(v.strip())
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: str) -> str:
        """Validate price."""
        if not v or not v.strip():
            raise ValueError("Price cannot be empty")
        return v.strip()
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize notes."""
        if v is None:
            return None
        return sanitize_notes(v.strip()) if v.strip() else None
    
    @classmethod
    def from_mongo(cls, doc: Dict[str, Any]) -> "ItemInDB":
        """
        Convert MongoDB document to ItemInDB model.
        
        Args:
            doc: MongoDB document dictionary
            
        Returns:
            ItemInDB instance
        """
        # Create a copy to avoid mutating the original dict
        doc = doc.copy()
        
        # Ensure URLs are strings (MongoDB stores them as strings)
        if doc.get("image") is not None:
            doc["image"] = str(doc["image"])
        if doc.get("url") is not None:
            doc["url"] = str(doc["url"])
        
        return cls(**doc)
    
    def to_mongo_dict(self) -> Dict[str, Any]:
        """
        Convert ItemInDB model to MongoDB document dict.
        
        Returns:
            Dictionary suitable for MongoDB storage
        """
        return self.model_dump(exclude_none=False)

