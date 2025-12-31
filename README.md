# Strategy Finder

Options Strategy Research Assistant - A web-based tool for extracting, analyzing, and synthesizing options trading strategy information from multiple sources.

## Quick Start

### Backend (Python FastAPI)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend (React + Vite)

```bash
cd frontend

# Install dependencies (already done during setup)
npm install

# Run dev server
npm run dev
```

### Access

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Environment Variables

Create `backend/.env` with:

```
GEMINI_API_KEY=your_gemini_api_key  # Required for LLM extraction
REDDIT_CLIENT_ID=your_reddit_id     # Optional for Reddit extraction
REDDIT_CLIENT_SECRET=your_secret    # Optional for Reddit extraction
```

## Features

- **URL Extraction**: Paste YouTube, Reddit, or article URLs
- **Specificity Scoring**: Rate how actionable the content is (1-10)
- **Trust Scoring**: Detect survivorship bias
- **Consensus View**: Compare multiple sources on the same strategy

## Tech Stack

- **Frontend**: Vite + React + TypeScript
- **Backend**: Python FastAPI
- **Database**: SQLite (async)
- **LLM**: Google Gemini

## Project Structure

```
/strategy-finder
├── /frontend         # React app
├── /backend          # FastAPI app
│   ├── /app
│   │   ├── /api      # API routes
│   │   ├── /extractors  # YouTube, Reddit, Article
│   │   ├── /synthesis   # Consensus logic
│   │   ├── /scoring     # Specificity & Trust
│   │   ├── /discovery   # Source discovery
│   │   └── /models      # Pydantic schemas
│   └── requirements.txt
└── README.md
```
