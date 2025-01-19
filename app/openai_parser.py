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

# Example usage
if __name__ == "__main__":
    sample_inner_text = """
    Awesome Product
    Price: $19.99
    """

    extracted_data = parse_inner_text_with_groq(sample_inner_text)
    print("Extracted Data:", extracted_data)
