# Reddit Social Listening Dashboard

Monitor public sentiment about **Taboola** and **Realize** on Reddit and Hacker News with AI-powered analysis.

## Features

- Multi-source data ingestion (Reddit + Hacker News)
- AI sentiment analysis (GPT-4o-mini)
- Field-level classification (Pricing, Performance, Support, etc.)
- Visual dashboard with filters and trends

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

cd frontend && npm install
```

### 2. Configure Environment

Create `.env` file:

```env
REDDIT_CLIENT_ID=your_id
REDDIT_SECRET_KEY=your_secret
REDDIT_USER_AGENT=SocialListeningAgent/1.0
OPENAI_API_KEY=your_key
```

## Running

```bash
# Backend (Terminal 1)
python api.py

# Frontend (Terminal 2)
cd frontend && npm run dev
```

- API: http://localhost:8080
- Dashboard: http://localhost:3000

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
├── api.py              # FastAPI backend
├── reddit_ingest.py    # Reddit data fetching
├── hackernews_ingest.py# HN data fetching
├── llm_validation.py   # AI sentiment analysis
├── ranking.py          # Engagement scoring
├── frontend/           # React dashboard
└── output/             # Generated JSON files
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rankings` | Get cached results |
| POST | `/api/refresh` | Fetch & analyze new data |
