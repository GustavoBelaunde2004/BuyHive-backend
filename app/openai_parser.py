import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

def parse_html_with_openai(html_content: str):
    """
    Send HTML content to OpenAI and extract product information.
    """
    prompt = f"""
    You are an AI assistant that extracts product details from raw HTML files of shopping websites.
    Extract the following details:
    1. Product Name
    2. Price
    3. Image URL

    HTML:
    {html_content}

    Provide the details as a JSON object with keys 'product_name', 'price', and 'image_url'.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        temperature=0
    )
    result = response.get("choices")[0].get("text").strip()
    return result