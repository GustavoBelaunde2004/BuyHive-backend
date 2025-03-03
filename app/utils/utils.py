def extract_product_name_from_url(url: str) -> str:
    """Extracts the product name from a URL by removing domain and numeric IDs."""
    from urllib.parse import urlparse

    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split("/")  # Extract path sections

    # Remove numeric segments (likely product IDs)
    words = [part for part in path_parts if not part.isdigit() and len(part) > 2]

    # Join cleaned segments
    product_name = " ".join(words).replace("-", " ").replace("_", " ").strip()
    #print(product_name)

    return product_name if product_name else "Unknown Product"