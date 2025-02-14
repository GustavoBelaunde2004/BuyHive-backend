import json
from groq import Groq

# Groq API key
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def parse_inner_text_with_groq(input_text: str):
    """
    Send plain innerText to Groq and extract product information.
    """
    if not isinstance(input_text, str) or not input_text.strip():
        raise ValueError("Invalid input: Expecting plain text input.")

    # Create a prompt for Groq
    prompt = f"""
    You are an AI that extracts product details from shopping website text.
    Analyze the following text and extract the following information:
    - Product Name
    - Price

    Provide the output as a JSON object with keys 'product_name' and 'price'.
    If a field is missing, use 'null' as the value.
    Remeber to only output the JSON, dont output anything else.

    Text:
    {input_text.strip()}
    """

    try:
        # Send the request to Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=500,
            temperature=0,
        )

        # Parse the response as JSON
        result = response.choices[0].message.content.strip()
        try:
            # Extract JSON content from Groq's response, ignoring formatting like triple backticks
            start_index = result.find("{")
            end_index = result.rfind("}") + 1

            if start_index == -1 or end_index == -1:
                raise ValueError("Groq response does not contain valid JSON.")

            # Extract and parse the JSON substring
            json_content = result[start_index:end_index]
            parsed_result = json.loads(json_content)
        except json.JSONDecodeError:
            raise ValueError(f"Groq returned invalid JSON: {result}")

        return parsed_result

    except Exception as e:
        raise ValueError(f"Error parsing text with Groq: {e}")
    

def parse_images_with_groq(image_urls: list):
    """
    Send an array of image URLs to Groq and determine the best product image.
    """
    if not isinstance(image_urls, list) or not image_urls:
        raise ValueError("Invalid input: Expecting a list of image URLs.")

    # Create a prompt for Groq
    prompt = f"""
    You are an AI assistant that selects the most relevant product image from a list of image URLs.
    Your goal is to determine which image is most likely to be the **main product image**.

    DONT RENDER THE IMAGES, JUST READ THE URL TO SAVE TIME.
    
    Consider the following factors:
    - Filename or URL patterns (avoid images with names like 'thumbnail', 'icon', 'placeholder', etc.).
    - If multiple images are equally relevant, pick the **first high-quality image**.
    
    Below is the list of image URLs, it is a plain text with all the URLs. Select the most relevant one and return only the chosen URL in JSON format:
    
    REMEMBER TO RETURN THE ANSWER IN A JSON, otherwise u get a little spank.

    Image URLs:
    {json.dumps(image_urls, indent=2)}
    
    **Output format:**
    {{
        "main_product_image": "selected_image_url"
    }}
    """

    try:
        # Send the request to Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=200,
            temperature=0.3,
        )

        # Parse the response as JSON
        result = response.choices[0].message.content.strip()
        try:
            # Extract JSON content from Groq's response
            start_index = result.find("{")
            end_index = result.rfind("}") + 1

            if start_index == -1 or end_index == -1:
                raise ValueError("Groq response does not contain valid JSON.")

            json_content = result[start_index:end_index]
            parsed_result = json.loads(json_content)

        except json.JSONDecodeError:
            raise ValueError(f"Groq returned invalid JSON: {result}")

        return parsed_result

    except Exception as e:
        raise ValueError(f"Error processing images with Groq: {e}")