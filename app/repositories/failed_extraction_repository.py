"""Failed Extraction repository for database operations."""
from typing import Dict, Any
from app.repositories.base import BaseRepository
from app.core.database import failed_extraction_collection


class FailedExtractionRepository(BaseRepository):
    """Repository for failed extraction database operations."""
    
    def __init__(self):
        super().__init__(failed_extraction_collection)
    
    async def create(self, extraction_data: Dict[str, Any]) -> str:
        """
        Create a new failed extraction entry.
        
        Args:
            extraction_data: Failed extraction document dictionary
            
        Returns:
            Extraction ID
        """
        await self.insert_one(extraction_data)
        return extraction_data.get("extraction_id")

