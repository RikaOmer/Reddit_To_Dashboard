# Design Document

## Architecture

```
Reddit API + HN API → Data Ingestion → LLM Validation → Ranking → FastAPI → React Dashboard
```

## Key Decisions

### LLM Choice
- **Model**: GPT-4o-mini (fast, cost-effective)
- **Temperature**: 0.1 (consistent output)
- **Format**: JSON response format for structured output

### Entity Disambiguation
- **Taboola**: Unique name, low false-positive risk
- **Realize**: Two-phase approach (capitalized + context keywords like "advertising", "platform")

### Engagement Score
```
score = upvotes × 1.0 + comments × 2.0 + upvote_ratio × 10
```

## Data Schema

### Post (items.jsonl)
```json
{
  "id": "abc123",
  "source": "reddit",
  "brand": "Taboola",
  "title": "...",
  "validation": {
    "is_relevant": true,
    "subject": "Performance",
    "sentiment": "positive",
    "sentiment_score": 0.7
  }
}
```

### Aggregates
```json
{
  "Taboola": {
    "total_posts": 25,
    "category_distribution": {...},
    "top_posts": [...]
  }
}
```

## Limitations

- No persistence (in-memory cache only)
- Reddit API rate limits
- English only
