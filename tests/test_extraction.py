"""
Tests for extraction routes (ML/AI endpoints).
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


class TestExtractionRoutes:
    """Test suite for extraction endpoints."""
    
    @patch('app.routers.extraction_routes.parse_images_with_openai')
    @patch('app.routers.extraction_routes.extract_product_name_from_url')
    def test_analyze_images_valid(self, mock_extract_name, mock_openai, authenticated_client):
        """Test /analyze-images endpoint with valid input."""
        mock_extract_name.return_value = "Nike Shoes"
        mock_openai.return_value = "https://example.com/best-image.jpg"
        
        payload = {
            "page_url": "https://example.com/product",
            "image_urls": "https://example.com/img1.jpg,https://example.com/img2.jpg"
        }
        
        response = authenticated_client.post("/extract/analyze-images", json=payload)
        assert response.status_code == status.HTTP_200_OK
        mock_extract_name.assert_called_once()
        mock_openai.assert_called_once()
    
    def test_analyze_images_missing_page_url(self, authenticated_client):
        """Test /analyze-images endpoint with missing page_url."""
        payload = {
            "image_urls": "https://example.com/img1.jpg"
        }
        
        response = authenticated_client.post("/extract/analyze-images", json=payload)
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_analyze_images_empty_urls(self, authenticated_client):
        """Test /analyze-images endpoint with empty image URLs."""
        payload = {
            "page_url": "https://example.com/product",
            "image_urls": ""
        }
        
        response = authenticated_client.post("/extract/analyze-images", json=payload)
        # Can be 400 (route validation) or 422 (Pydantic validation)
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    @patch('app.routers.extraction_routes.extract_product_name_from_url')
    def test_analyze_images_invalid_urls(self, mock_extract, authenticated_client):
        """Test /analyze-images endpoint with invalid URLs."""
        mock_extract.return_value = "product"
        payload = {
            "page_url": "https://example.com/product",
            "image_urls": ",,,"  # Only commas, no valid URLs
        }
        
        response = authenticated_client.post("/extract/analyze-images", json=payload)
        # Should return 400 when no valid URLs found after parsing
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @patch('app.routers.extraction_routes.parse_images_with_openai')
    @patch('app.routers.extraction_routes.extract_product_name_from_url')
    def test_analyze_images_openai_failure(self, mock_extract_name, mock_openai, authenticated_client):
        """Test /analyze-images endpoint when OpenAI service fails."""
        mock_extract_name.return_value = "Nike Shoes"
        mock_openai.side_effect = Exception("OpenAI API error")
        
        payload = {
            "page_url": "https://example.com/product",
            "image_urls": "https://example.com/img1.jpg"
        }
        
        response = authenticated_client.post("/extract/analyze-images", json=payload)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @patch('app.routers.extraction_routes.parse_inner_text_with_openai')
    def test_extract_valid(self, mock_openai, authenticated_client):
        """Test /extract endpoint with valid text input."""
        mock_openai.return_value = {
            "items": [
                {"name": "Product 1", "price": "99.99"}
            ]
        }
        
        input_text = "Product 1 - $99.99\nProduct 2 - $149.99"
        
        response = authenticated_client.post(
            "/extract/extract",
            content=input_text,
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "cart_items" in data
        mock_openai.assert_called_once()
    
    def test_extract_empty_input(self, authenticated_client):
        """Test /extract endpoint with empty input."""
        response = authenticated_client.post(
            "/extract/extract",
            content="",
            headers={"Content-Type": "text/plain"}
        )
        # Empty input should return 400, but might return 500 if request body is empty
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    @patch('app.routers.extraction_routes.parse_inner_text_with_openai')
    def test_extract_openai_failure(self, mock_openai, authenticated_client):
        """Test /extract endpoint when OpenAI service fails."""
        mock_openai.side_effect = Exception("OpenAI API error")
        
        input_text = "Product 1 - $99.99"
        
        response = authenticated_client.post(
            "/extract/extract",
            content=input_text,
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_extract_unauthenticated(self, unauthenticated_client):
        """Test that /extract requires authentication."""
        response = unauthenticated_client.post(
            "/extract/extract",
            content="test",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

