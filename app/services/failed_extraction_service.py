"""Failed Extraction service for business logic."""
from datetime import datetime
from uuid import uuid4
from typing import Dict
from urllib.parse import urlparse
from app.repositories.failed_page_extraction_repository import FailedPageExtractionRepository
from app.repositories.failed_item_extraction_repository import FailedItemExtractionRepository
from app.models.failed_page_extraction import FailedPageExtraction
from app.models.failed_item_extraction import FailedItemExtraction


class FailedExtractionService:
    """Service for failed extraction business logic."""
    
    def __init__(
        self,
        page_extraction_repo: FailedPageExtractionRepository,
        item_extraction_repo: FailedItemExtractionRepository
    ):
        """
        Initialize failed extraction service with repositories.
        
        Args:
            page_extraction_repo: Failed page extraction repository instance
            item_extraction_repo: Failed item extraction repository instance
        """
        self.page_extraction_repo = page_extraction_repo
        self.item_extraction_repo = item_extraction_repo
    
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
    
    async def submit_failed_page_extraction(
        self,
        url: str,
        failure_type: str,
        confidence: float
    ) -> Dict:
        """
        Submit failed page extraction (save to MongoDB).
        
        Args:
            url: URL that failed page extraction
            failure_type: Type of failure (e.g., "unsupported", "no_product")
            confidence: Confidence that this is a failure (0.0-1.0)
            
        Returns:
            Dictionary with success message and extraction_id
        """
        extraction_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        
        # Extract domain from URL
        domain = self._extract_domain(url)
        
        # Create FailedPageExtraction instance
        failed_extraction = FailedPageExtraction(
            extraction_id=extraction_id,
            url=str(url),
            domain=domain,
            failure_type=failure_type,
            confidence=confidence,
            timestamp=now,  # Server-generated timestamp
            created_at=now,
        )
        
        # Convert to MongoDB dict and save
        extraction_doc = failed_extraction.to_mongo_dict()
        await self.page_extraction_repo.create(extraction_doc)
        
        return {"status": "success"}
    
    async def submit_failed_item_extraction(
        self,
        url: str,
        type: str,
        image_confidence: float,
        name_confidence: float,
        price_confidence: float
    ) -> Dict:
        """
        Submit failed item extraction (save to MongoDB).
        
        Args:
            url: URL of the page where item extraction failed
            type: Type of failure (e.g., "maybe", "not_a_product")
            image_confidence: Confidence for image extraction (0.0-1.0)
            name_confidence: Confidence for name extraction (0.0-1.0)
            price_confidence: Confidence for price extraction (0.0-1.0)
            
        Returns:
            Dictionary with success message and extraction_id
        """
        extraction_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        
        # Extract domain from URL
        domain = self._extract_domain(url)
        
        # Create FailedItemExtraction instance
        failed_extraction = FailedItemExtraction(
            extraction_id=extraction_id,
            url=str(url),
            domain=domain,
            type=type,
            image_confidence=image_confidence,
            name_confidence=name_confidence,
            price_confidence=price_confidence,
            timestamp=now,  # Server-generated timestamp
            created_at=now,
        )
        
        # Convert to MongoDB dict and save
        extraction_doc = failed_extraction.to_mongo_dict()
        await self.item_extraction_repo.create(extraction_doc)
        
        return {"status": "success"}

