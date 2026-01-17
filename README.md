# BuyHive Backend 🐝

> The backend API powering BuyHive - an intelligent e-commerce browser extension

[Check BuyHive's frontend here!](https://github.com/GustavoBelaunde2004/buy-hive)

**Note**: This is proprietary software. See [LICENSE](./LICENSE) for details.

## About

BuyHive-backend is the core API service for BuyHive, a browser extension that helps users manage shopping carts across multiple e-commerce sites. This FastAPI-based backend handles cart management, product extraction, image verification, and user authentication.

## Architecture

### Core Features

- **Cart Management**: Multi-cart system with full CRUD operations
- **Item Management**: Add, edit, and organize items across carts
- **User Management**: Auth0-based authentication and user profiles
- **Product Extraction**: AI-powered extraction from e-commerce URLs using Groq and OpenAI
- **Feedback System**: Bug reports and feature requests (MongoDB + Google Sheets)

### Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB Atlas (via `motor`)
- **AI/ML**: OpenAI (GPT-4o, Vision API), Groq
- **Authentication**: Auth0
- **Email**: AWS SES (optional, for cart sharing)
- **Deployment**: Railway (via Docker)
- **CI/CD**: GitHub Actions
- **Other Libraries**: pandas, scikit-learn, requests, beautifulsoup4, lxml, httpx

## Deployment

The application is deployed on **Railway** using Docker. 
**Note**: Deployment is handled entirely by Railway - no AWS infrastructure is required for deployment. AWS is only used optionally for email service (SES).

## Documentation

**API Documentation**: Interactive API documentation is available when the server is running:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
