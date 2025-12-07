"""
Tests for extraction routes (ML/AI endpoints).
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


class TestExtractionRoutes:
    """Test suite for extraction endpoints."""
    
    @patch('app.routers.extraction_routes.verify_image_with_clip')
    def test_verify_image_valid(self, mock_clip, authenticated_client):
        """Test /verify-image endpoint with valid image."""
        mock_clip.return_value = True
        
        payload = {
            "product_name": "Nike Shoes",
            "price": "99.99",
            "image_url": "https://example.com/image.jpg"
        }
        
        response = authenticated_client.post("/extract/verify-image", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "product_name" in data
        assert "price" in data
        assert "verified_image_url" in data
        assert data["verified_image_url"] == payload["image_url"]  # Valid image returned
        mock_clip.assert_called_once()
    
    @patch('app.routers.extraction_routes.verify_image_with_clip')
    def test_verify_image_invalid(self, mock_clip, authenticated_client):
        """Test /verify-image endpoint with invalid image."""
        mock_clip.return_value = False
        
        payload = {
            "product_name": "Nike Shoes",
            "price": "99.99",
            "image_url": "https://example.com/wrong-image.jpg"
        }
        
        response = authenticated_client.post("/extract/verify-image", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "verified_image_url" in data
        assert data["verified_image_url"] == "https://example.com/default.jpg"  # Default image
    
    def test_verify_image_missing_product_name(self, authenticated_client):
        """Test /verify-image endpoint with missing product_name."""
        payload = {
            "price": "99.99",
            "image_url": "https://example.com/image.jpg"
        }
        
        response = authenticated_client.post("/extract/verify-image", json=payload)
        # Should return 422 (validation error) or 400
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_verify_image_missing_image_url(self, authenticated_client):
        """Test /verify-image endpoint with missing image_url."""
        payload = {
            "product_name": "Nike Shoes",
            "price": "99.99"
        }
        
        response = authenticated_client.post("/extract/verify-image", json=payload)
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    @patch('app.routers.extraction_routes.verify_image_with_clip')
    def test_verify_image_clip_failure(self, mock_clip, authenticated_client):
        """Test /verify-image endpoint when CLIP service fails."""
        mock_clip.side_effect = Exception("CLIP model error")
        
        payload = {
            "product_name": "Nike Shoes",
            "price": "99.99",
            "image_url": "https://example.com/image.jpg"
        }
        
        response = authenticated_client.post("/extract/verify-image", json=payload)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_verify_image_unauthenticated(self, unauthenticated_client):
        """Test that /verify-image requires authentication."""
        payload = {
            "product_name": "Nike Shoes",
            "price": "99.99",
            "image_url": "https://example.com/image.jpg"
        }
        
        response = unauthenticated_client.post("/extract/verify-image", json=payload)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
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
    
    @patch('app.routers.extraction_routes.predict_product_page')
    def test_classify_url_product_page(self, mock_bert, authenticated_client):
        """Test /classify-url endpoint with product page URL."""
        mock_bert.return_value = 1
        
        payload = {
            "url": "https://example.com/products/nike-shoes"
        }
        
        response = authenticated_client.post("/extract/classify-url", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "url" in data
        assert "is_product_page" in data
        assert data["is_product_page"] is True
        mock_bert.assert_called_once()
    
    @patch('app.routers.extraction_routes.predict_product_page')
    def test_classify_url_non_product_page(self, mock_bert, authenticated_client):
        """Test /classify-url endpoint with non-product page URL."""
        mock_bert.return_value = 0
        
        payload = {
            "url": "https://example.com/about"
        }
        
        response = authenticated_client.post("/extract/classify-url", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_product_page"] is False
    
    @patch('app.routers.extraction_routes.predict_product_page')
    def test_classify_url_bert_unavailable(self, mock_bert, authenticated_client):
        """Test /classify-url endpoint when BERT model is unavailable."""
        mock_bert.side_effect = ValueError("BERT model is not available")
        
        payload = {
            "url": "https://example.com/products/item"
        }
        
        response = authenticated_client.post("/extract/classify-url", json=payload)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert "BERT model not available" in data.get("detail", "")
    
    def test_classify_url_missing_url(self, authenticated_client):
        """Test /classify-url endpoint with missing URL."""
        payload = {}
        
        response = authenticated_client.post("/extract/classify-url", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_classify_url_unauthenticated(self, unauthenticated_client):
        """Test that /classify-url requires authentication."""
        payload = {
            "url": "https://example.com/product"
        }
        
        response = unauthenticated_client.post("/extract/classify-url", json=payload)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

