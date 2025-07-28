# Extension Backend

This project contains a FastAPI-based backend used by the browser extension.

## Prerequisites

- Python 3.10 or later
- `pip` for installing dependencies

## Installation

1. Clone this repository.
2. Create and activate a virtual environment (recommended).
3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root or export the following variables in your environment. The application reads them via `config.py`.

```env
MONGO_URL=<your Mongo connection string>
GROQ_API_KEY=<your GROQ API key>
GMAIL_USER=<gmail user>
GMAIL_PASSWORD=<gmail password>
OPENAI_API_KEY=<your OpenAI API key>
GOOGLE_SEARCH_API=<Google search API key>
CSE_ID=<Google custom search engine ID>
```

## Running the Server

Start the FastAPI server using `uvicorn`:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000` by default.
