import requests
import pandas as pd
#from config import CSE_ID,GOOGLE_SEARCH_API
import time

# Your Google API credentials (Replace these with your actual API key and CX ID)
#API_KEY = GOOGLE_SEARCH_API  # Replace with your actual API key
#CX = CSE_ID  # Replace with your Custom Search Engine ID (CSE ID)

# 🔹 List of products to search for
product_queries = [
        "buy office chair", "buy mountain bike", "buy DSLR camera", "buy camping tent", 
        "buy power bank", "buy electric scooter", "buy baby stroller", "buy skateboard", 
        "buy gym weights", "buy hair dryer", "buy wireless charger", "buy swimsuit", 
        "buy smart home door lock", "buy pressure washer", "buy protein powder", "buy hiking backpack", 
        "buy video doorbell", "buy bike helmet", "buy pet food", "buy smart mirror"
    ]
# Sites to scrape
sites = ["amazon.com","walmart.com", "ebay.com", "bestbuy.com", "aliexpress.com"]

# Initialize data storage
all_product_urls = []

# Loop through each product search
for product in product_queries:
    query = f"{product} site:" + " OR site:".join(sites)
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx=b514a90b9b0d24f1f&key=AIzaSyBcqNasu0z6Vbs2dUQxdOmb5NzMYJRPAbY"

    print(f"🔍 Searching: {query}")
    
    try:
        response = requests.get(url)
        data = response.json()

        # Extract product URLs
        for item in data.get("items", []):
            page_url = item.get("link", "")
            if page_url:
                all_product_urls.append((page_url, 1))  # Label as product page (1)

        # Wait to avoid rate limits
        time.sleep(2)  # Avoid hitting Google API limits

    except Exception as e:
        print(f"❌ Error fetching results for {product}: {e}")

# Convert to DataFrame
df = pd.DataFrame(all_product_urls, columns=["url", "label"])

# Save to CSV (append mode to keep adding new data)
df.to_csv("ecommerce_urls.csv", mode="a", header=False, index=False)

print("✅ Shopping URLs added to ecommerce_urls.csv")