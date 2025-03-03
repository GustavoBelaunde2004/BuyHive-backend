import json
import requests
import pandas as pd
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config import CSE_ID,GOOGLE_SEARCH_API

# Your Google API credentials (Replace these with your actual API key and CX ID)
#API_KEY = GOOGLE_SEARCH_API  # Replace with your actual API key
#CX = CSE_ID  # Replace with your Custom Search Engine ID (CSE ID)

# Filtering functions
def is_product_page(url):
    product_keywords = ["/dp/", "/gp/", "/p/", "/product/", "/sku/", "/id/", "/item/", "/shop/", "/buy/"]
    return any(keyword in url.lower() for keyword in product_keywords)

def is_non_product_page(url):
    non_product_keywords = ["/blog/", "/news/", "/help/", "/faq/", "/support/", "/search/", "/category/", "/collections/"]
    return any(keyword in url.lower() for keyword in non_product_keywords)

# Scrape function
def get_urls(query, label, sites):
    all_urls = []
    search_query = f"{query} site:" + " OR site:".join(sites)
    url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&cx={CSE_ID}&key={GOOGLE_SEARCH_API}"

    try:
        response = requests.get(url)
        data = response.json()
        print(json.dumps(data, indent=2))  # Pretty print response

        for item in data.get("items", []):
            page_url = item.get("link", "")

            # Apply filters
            if label == 1 and is_product_page(page_url):  # Product pages only
                all_urls.append((page_url, 1))
            elif label == 0 and is_non_product_page(page_url):  # Non-product pages only
                all_urls.append((page_url, 0))

        time.sleep(2)  # Prevent API rate limit issues
    except Exception as e:
        print(f"❌ Error fetching results for {query}: {e}")

    return all_urls

# Run scraping
data = []
sites = [
    "ebay.com", "walmart.com", "bestbuy.com", "target.com",
    "newegg.com", "bhphotovideo.com", "aliexpress.com", "costco.com", "homedepot.com",
    "lowes.com", "wayfair.com", "macys.com", "nordstrom.com", "kohl’s.com",
    "nike.com", "adidas.com", "underarmour.com", "reebok.com", "puma.com",
    "hollisterco.com", "abercrombie.com", "lulus.com", "urbanoutfitters.com", "zappos.com",
    "gap.com", "uniqlo.com", "hoka.com", "asics.com", "fila.com"
]
product_queries = [
    "buy iPhone 15", "buy MacBook Pro", "best price PlayStation 5", "Samsung Galaxy S23 add to cart",
    "purchase AirPods Pro", "Xbox Series X buy online", "buy Bose Headphones", "best price Smart TV",
    "cheap Gaming Laptop deal", "buy Apple Watch official store", "order Nike Air Force 1",
    "buy Adidas Ultraboost", "purchase Samsung Tablet", "get Sony WH-1000XM5", "discount Google Pixel",
    "shop Dell XPS laptop", "online deal Canon DSLR", "cheap gaming mouse", "get Apple Magic Keyboard",
    "buy Razer Mechanical Keyboard", "best price Lenovo ThinkPad", "get Jabra Elite Earbuds",
    "buy GoPro Hero 11", "purchase Sony OLED TV", "best deal LG Soundbar", "online deal Fossil Smartwatch",
    "cheap TCL Smart TV", "get Samsung Galaxy Buds Pro", "buy Dyson Hair Dryer", "best deal KitchenAid Mixer",
    "cheap iPad Pro deal", "get HP Envy Laptop", "purchase Bose QuietComfort Earbuds",
    "shop discount Garmin Watch", "buy Google Nest Hub", "best price Sonos Soundbar",
    "buy Beats Studio Headphones", "purchase Samsung QLED TV", "get HyperX Gaming Headset",
    "order Logitech MX Master 3", "cheap Philips Air Fryer", "buy Nintendo Switch OLED",
    "best deal DJI Mini Drone", "get Kindle Paperwhite", "shop Sony PlayStation VR2",
    "buy Apple HomePod Mini", "order Samsung Smart Monitor", "best price ASUS ROG Laptop",
    "buy Corsair Gaming Keyboard", "purchase Seagate External SSD", "get Samsung Curved Monitor",
    "order Sony Alpha Mirrorless Camera", "buy LG Gram Ultrabook", "cheap Brother Laser Printer",
    "shop Apple Mac Mini M2", "get Lenovo Legion Gaming PC", "best deal Acer Predator Monitor",
    "buy SteelSeries Wireless Headset", "purchase Rode Podcast Microphone",
    "order Blue Yeti USB Mic", "cheap Microsoft Surface Laptop", "get Bose Smart Speaker",
    "shop Asus TUF Gaming Laptop", "buy Alienware Gaming PC", "best price BenQ Gaming Monitor",
    "buy Logitech G Pro Mouse", "purchase Garmin Fenix 7", "order Samsung Smart Fridge",
    "shop LG UltraFine Monitor", "get GoPro Max 360", "buy Amazon Echo Dot", "cheap JBL Bluetooth Speaker",
    "purchase Razer Gaming Laptop", "order Meta Quest VR Headset", "best price Shark Robot Vacuum",
    "shop ASUS ZenBook Pro", "buy Logitech StreamCam", "get Tile Bluetooth Tracker",
    "purchase Elgato Stream Deck", "order Fitbit Sense 2", "shop Yamaha Soundbar",
    "get Panasonic 4K TV", "buy Dell G5 Gaming PC", "best deal Sony Xperia Phone",
    "purchase Western Digital External HDD", "order Alienware 360Hz Monitor",
    "cheap OnePlus Nord Phone", "buy Roku Streaming Stick", "shop Epson EcoTank Printer",
    "get Google Chromecast 4K", "purchase Lenovo Yoga Convertible", "order Samsung Galaxy Chromebook",
    "shop TCL 6-Series TV", "get Ring Doorbell Pro", "best price Bose Sleepbuds"
]
non_product_queries = ["latest tech news", "best fashion trends", "how to buy a laptop guide"]

for query in product_queries:
    data.extend(get_urls(query, 1, sites))  # Product pages (1)
for query in non_product_queries:
    data.extend(get_urls(query, 0, sites))  # Non-product pages (0)

# Save to CSV
df = pd.DataFrame(data, columns=["url", "label"])
df.to_csv("ecommerce_urls.csv", mode="a", header=False, index=False)

print("✅ New filtered URLs added to ecommerce_urls.csv")