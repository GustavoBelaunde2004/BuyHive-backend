from bs4 import BeautifulSoup
import json

def preprocess_html(html_content: str) -> list:
    """Extract universal features from HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Try extracting JSON-LD for structured data (if present)
    json_ld_data = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            json_ld_data.append(json.loads(script.string))
        except (TypeError, json.JSONDecodeError):
            continue

    elements = soup.find_all()
    features = []

    for element in elements:
        # Extract universal features
        feature = {
            "tag": element.name,
            "attributes": " ".join([f"{k}={v}" for k, v in element.attrs.items()]),
            "text_length": len(element.text.strip()),
            "position": elements.index(element)  # Position in the DOM
        }
        features.append(feature)

    return {"features": features, "json_ld": json_ld_data}