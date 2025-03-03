import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

# Example search URL for Amazon
search_url = "https://www.amazon.com/s?k=electronics"

def get_links(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = []
    for link in soup.find_all('a', href=True):
        full_url = "https://www.amazon.com" + link['href']
        links.append(full_url)

    return links

urls = get_links(search_url)

# Label URLs as product pages (1) or non-product pages (0)
data = []
for url in urls:
    if "/dp/" in url:  # Amazon product pages have /dp/
        data.append((url, 1))
    else:
        data.append((url, 0))

# Save to CSV
df = pd.DataFrame(data, columns=["url", "label"])
df.to_csv("ecommerce_urls.csv", index=False)

print("Dataset saved as ecommerce_urls.csv")
