# BuyHive-backend  🐝

[Check BuyHive's frontend here!](https://github.com/GustavoBelaunde2004/buy-hive)

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
- **Database**: MongoDB Atlas (via `motor`)
- **Email**: AWS SES (migrated from Gmail SMTP)
- **Deployment**: Docker, AWS ECS Fargate
- **CI/CD**: GitHub Actions
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
   - AWS credentials (for SES email)

## Running the Server

### Local Development

```sh
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

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

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy to AWS

1. Follow [AWS_CONSOLE_SETUP.md](./AWS_CONSOLE_SETUP.md) for AWS setup
2. Push to `main` branch - CI/CD will automatically deploy
3. Or manually deploy using `scripts/deploy.sh`

## Documentation

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment guide
- [AWS_CONSOLE_SETUP.md](./AWS_CONSOLE_SETUP.md) - Step-by-step AWS setup
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - API reference
- [RUNBOOK.md](./RUNBOOK.md) - Operations guide

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
