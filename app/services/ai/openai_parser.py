import json
from openai import OpenAI
from app.core.config import settings

# Create OpenAI client instance
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def parse_inner_text_with_openai(input_text: str) -> dict:
    """
    Send plain innerText to OpenAI and extract product information.
    
    Returns:
        dict: Dictionary with 'product_name' and 'price' keys
    """
    if not isinstance(input_text, str) or not input_text.strip():
        raise ValueError("Invalid input: Expecting plain text input.")

    # Create a prompt for OpenAI
    prompt = f"""
    You are an AI that extracts product details from shopping website text.
    Analyze the following text and extract the following information:
    - Product Name
    - Price

    Provide the output as a JSON object with keys 'product_name' and 'price'.
    If a field is missing, use 'null' as the value.
    Remember to only output the JSON, don't output anything else.

    Text:
    {input_text.strip()}
    """

    try:
        # Send the request to OpenAI using the new client API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0,
        )

        # Parse the response as JSON
        result = response.choices[0].message.content.strip()
        try:
            # Extract JSON content from OpenAI's response
            start_index = result.find("{")
            end_index = result.rfind("}") + 1

            if start_index == -1 or end_index == -1:
                raise ValueError("OpenAI response does not contain valid JSON.")

            json_content = result[start_index:end_index]
            parsed_result = json.loads(json_content)
        except json.JSONDecodeError:
            raise ValueError(f"OpenAI returned invalid JSON: {result}")

        return parsed_result

    except Exception as e:
        raise ValueError(f"Error parsing text with OpenAI: {e}")

def parse_images_with_openai(page_url: str, product_name: str, image_urls: list) -> str:
    """
    Uses OpenAI to determine the best product image based on the page URL and product name.
    
    Returns:
        str: The selected image URL
    """
    if not isinstance(image_urls, list) or not image_urls:
        raise ValueError("Invalid input: Expecting a list of image URLs.")

    # Create a prompt for OpenAI
    prompt = f"""
    You are an AI assistant that selects the most relevant product image from a list of image URLs.
    **Page URL:** {page_url}
    **Product Name:** {product_name}
    Your goal is to determine which image is most likely to be the **main product image**.
    Below is the list of image URLs. Select the most relevant one and return only the chosen URL as plain text.
    **Image URLs:**
    {json.dumps(image_urls, indent=2)}
    **Output format:**
    Just return the selected image URL as plain text. No JSON, no additional explanation.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=85,
            temperature=0.3,
        )

        result = response.choices[0].message.content.strip()

        if not result.startswith("http"):
            raise ValueError(f"OpenAI returned an invalid URL: {result}")

        return result

    except Exception as e:
        raise ValueError(f"Error processing images with OpenAI: {e}")