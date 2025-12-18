# BuyHive-backend  🐝

[Check BuyHive's frontend here!](https://github.com/GustavoBelaunde2004/buy-hive)

## Overview

BuyHive-backend is a FastAPI-based backend for an e-commerce browser extension. It provides APIs for cart management, item handling, user management, product extraction, and image verification. The backend leverages AI models (OpenAI, CLIP, BERT) to analyze product images and classify URLs, supporting advanced product extraction and verification from various e-commerce sites.

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
- **Database**: MongoDB Atlas (via `motor`)
- **Email**: AWS SES (optional, for cart sharing via email)
- **Deployment**: Railway (via Docker)
- **CI/CD**: GitHub Actions
- **Other Libraries**: pandas, scikit-learn, requests, beautifulsoup4, lxml, etc.

## Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/GustavoBelaunde2004/BuyHive-backend.git
   cd BuyHive-backend
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

   Copy `.env.example` to `.env` and fill in your values:
   ```sh
   cp .env.example .env
   ```
   
   See `.env.example` for all required variables. Minimum required:
   - `MONGO_URL` - MongoDB connection string
   - `AUTH0_DOMAIN` - Auth0 tenant domain
   - `AUTH0_AUDIENCE` - Auth0 API identifier
   - `ALLOWED_ORIGINS` - Comma-separated allowed origins
   - `GROQ_API_KEY` - Groq API key
   - `OPENAI_API_KEY` - OpenAI API key
   
   **Optional** (for email functionality):
   - AWS SES credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `SES_FROM_EMAIL`) - Only needed if you want to enable email features like cart sharing

## Running the Server

### Local Development

```sh
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.

### Using Docker

```sh
# Build image
docker build -t buyhive-backend:latest .

# Run container
docker run -p 8000:8000 --env-file .env buyhive-backend:latest
```

### Using Docker Compose (with MongoDB)

```sh
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Deployment

The application is deployed on **Railway** using Docker. See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

**Note**: Deployment is handled entirely by Railway - no AWS infrastructure is required for deployment. AWS is only used optionally for email service (SES).

## Documentation

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment guide
- [RUNBOOK.md](./RUNBOOK.md) - Operations guide
- [TESTING.md](./TESTING.md) - Testing guide
- [AUTH0_SETUP.md](./AUTH0_SETUP.md) - Auth0 configuration guide

**API Documentation**: Once the server is running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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
