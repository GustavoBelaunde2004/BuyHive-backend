"""Failed Extraction service for business logic."""
from datetime import datetime
from uuid import uuid4
from typing import Dict
from urllib.parse import urlparse
from app.repositories.failed_extraction_repository import FailedExtractionRepository
from app.models.failed_extraction import FailedExtraction


class FailedExtractionService:
    """Service for failed extraction business logic."""
    
    def __init__(self, extraction_repo: FailedExtractionRepository):
        """
        Initialize failed extraction service with repository.
        
        Args:
            extraction_repo: Failed extraction repository instance
        """
        self.extraction_repo = extraction_repo
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: Full URL
            
        Returns:
            Domain name (e.g., "amazon.com")
        """
        parsed = urlparse(str(url))
        domain = parsed.netloc
        
        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
        
        # Convert to lowercase
        domain = domain.lower()
        
        return domain
    
    async def submit_failed_extraction(
        self,
        url: str,
        user_id: str
    ) -> Dict:
        """
        Submit failed extraction (save to MongoDB).
        
        Args:
            url: URL that failed extraction
            user_id: User ID who encountered the failure
            
        Returns:
            Dictionary with success message and extraction_id
        """
        extraction_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        
        # Extract domain from URL
        domain = self._extract_domain(url)
        
        # Create FailedExtraction instance
        failed_extraction = FailedExtraction(
            extraction_id=extraction_id,
            url=str(url),
            domain=domain,
            user_id=user_id,
            timestamp=now,  # Server-generated timestamp
            created_at=now,
        )
        
        # Convert to MongoDB dict and save
        extraction_doc = failed_extraction.to_mongo_dict()
        await self.extraction_repo.create(extraction_doc)
        
        return {
            "message": "Failed extraction recorded successfully",
            "extraction_id": extraction_id
        }

