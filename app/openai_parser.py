import openai
from bs4 import BeautifulSoup

openai.api_key = "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"

def trim_html(html_content: str) -> str:
    """
    Extracts the <body> content from the HTML document to reduce size.
    Falls back to the full HTML if <body> is not found.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        body = soup.body
        if body:
            return str(body)
        else:
            return html_content  # Fallback to the full HTML
    except Exception as e:
        # Log the error and fallback to the original HTML
        print(f"Error trimming HTML: {e}")
        return html_content

def parse_html_with_openai(html_content: str):
    """
    Send trimmed HTML content to OpenAI and extract product information.
    """
    # Trim the HTML before sending to OpenAI
    trimmed_html = trim_html(html_content)

    # Create a robust prompt
    prompt = f"""
    You are an AI that extracts product details from HTML files of shopping websites.
    Analyze the provided HTML and extract the following information:
    - Product Name
    - Price
    - Image URL (if available)

    Provide the output as a JSON object with keys 'product_name', 'price', and 'image_url'.
    If a field is missing, use 'null' as the value.

    HTML:
    {trimmed_html}
    """

    try:
        # Send the request to OpenAI
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=500,
            temperature=0,
        )
        result = response.choices[0].text.strip()

        # Convert the result to JSON
        return result
    except Exception as e:
        raise ValueError(f"Error parsing HTML with OpenAI: {e}")
