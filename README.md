# Extension-backend

## Overview

Extension-backend is a FastAPI-based backend for an e-commerce browser extension. It provides APIs for cart management, item handling, user management, product extraction, and image verification. The backend leverages AI models (OpenAI, CLIP, BERT) to analyze product images and classify URLs, supporting advanced product extraction and verification from various e-commerce sites.

## Features

- **Cart Management**: Create, edit, retrieve, and delete user carts.
- **Item Management**: Add, edit, retrieve, and delete items in carts.
- **User Management**: Add users and share carts via email.
- **Product Extraction**: Extract product information and images from URLs using AI models.
- **Image Verification**: Verify product images using CLIP and OpenAI.
- **URL Classification**: Classify e-commerce URLs using BERT.

## Tech Stack

- **Backend Framework**: FastAPI
- **AI/ML**: OpenAI, CLIP, BERT (HuggingFace Transformers, TensorFlow, PyTorch)
- **Database**: MongoDB (via `motor`)
- **Email**: Gmail SMTP (via `yagmail`)
- **Other Libraries**: pandas, scikit-learn, requests, beautifulsoup4, lxml, etc.

## Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/GustavoBelaunde2004/Extension-backend.git
   cd Extension-backend
   ```

2. **Create and activate a Python virtual environment**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the root directory with the following variables:
   ```
   MONGO_URL=your_mongodb_url
   GROQ_API_KEY=your_groq_api_key
   GMAIL_USER=your_gmail_address
   GMAIL_PASSWORD=your_gmail_password
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_SEARCH_API=your_google_search_api_key
   CSE_ID=your_custom_search_engine_id
   ```

## Running the Server

```sh
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## Example Usage

- **Add a user**
  ```
  POST /users/add
  {
    "email": "user@example.com",
    "name": "John Doe"
  }
  ```

- **Create a cart**
  ```
  POST /carts/{email}
  {
    "cart_name": "My Cart"
  }
  ```

- **Add item to cart**
  ```
  POST /carts/{email}/{cart_id}/items
  {
    "product_name": "Nike Shoes",
    "price": 99.99,
    "image": "https://example.com/image.jpg",
    "url": "https://nike.com/shoes"
  }
  ```

- **Verify product image**
  ```
  POST /verify-image
  {
    "product_name": "Nike Shoes",
    "price": 99.99,
    "image_url": "https://example.com/image.jpg"
  }
  ```