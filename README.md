# Social Listening Dashboard

Monitor public sentiment about **Taboola** and **Realize** on Reddit and Hacker News with AI-powered analysis.

## Features

- **Multi-source ingestion**: Reddit API + Hacker News API
- **AI sentiment analysis**: GPT-4o-mini with structured JSON output
- **Field-level classification**: Pricing, Performance, Support, UX, Integration, General
- **Visual dashboard**: Filter by platform, entity, and topic; view trends over time
- **Aggregates**: Sentiment distribution, top themes with representative quotes

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/RikaOmer/Reddit_To_Dashboard.git
cd Reddit_To_Dashboard
```

### 2. Install Dependencies

**Backend:**

**Virtual Environment (Recommended)**
```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Linux/Mac:** `source venv/bin/activate`

Then install dependencies:
```bash
pip install -r requirements.txt
```


**Frontend:**
```bash
cd frontend
npm install
```

### 3. Configure Environment

Create `.env` file in project root:

```env
REDDIT_CLIENT_ID=your_id
REDDIT_SECRET_KEY=your_secret
REDDIT_USER_AGENT=SocialListeningAgent/1.0
OPENAI_API_KEY=your_key
```

### 4. Run

**Terminal 1 - Backend API: (Make sure you are still in venv)**
```bash
python api.py
```

**Terminal 2 - Frontend Dashboard: (Make sure you are still in venv)**
```bash
cd frontend
npm run dev
```

- **API**: http://localhost:8080
- **Dashboard**: http://localhost:3000

## Testing

```bash
pytest tests/ -v
```

## Output Files

| File | Description |
|------|-------------|
| `output/items.jsonl` | Individual posts with sentiment analysis |
| `output/aggregates.json` | Aggregated metrics per entity |

### Sample Item Schema

```json
{
  "id": "abc123",
  "source": "reddit",
  "brand": "Taboola",
  "title": "Post title",
  "validation": {
    "is_relevant": true,
    "subject": "Performance",
    "sentiment": "positive",
    "sentiment_score": 0.7
  }
}
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rankings` | Get cached results with aggregates |
| POST | `/api/refresh` | Fetch & analyze fresh data |

## Project Structure

```
├── api.py               # FastAPI backend server
├── reddit_ingest.py     # Reddit data fetching (PRAW)
├── hackernews_ingest.py # Hacker News API integration
├── llm_validation.py    # OpenAI sentiment analysis
├── ranking.py           # Engagement scoring algorithm
├── frontend/            # React + Vite dashboard
├── output/              # Generated JSON output files
├── tests/               # Unit tests
├── DESIGN.md            # Architecture & design decisions
└── requirements.txt     # Python dependencies
```

## Design Document

See [DESIGN.md](DESIGN.md) for:
- Architecture diagram
- LLM prompt design & schema constraints
- Entity disambiguation approach
- Limitations & next steps

## Limitations & Edge Cases

- **Sarcasm**: LLM may misclassify sarcastic posts
- **Mixed sentiment**: Posts with multiple sentiments use dominant tone
- **"Realize" disambiguation**: Uses capitalization + context keywords to avoid false positives
- **Rate limits**: Reddit API has usage limits; cached results reduce API calls
- **English only**: Analysis optimized for English content

## Compliance

This project only uses publicly available content and respects platform Terms of Service. No private data is accessed or stored.
