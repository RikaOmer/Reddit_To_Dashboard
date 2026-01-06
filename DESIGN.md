# Design Document

## Problem & Success Criteria

### Problem
Taboola needs to understand public perception of its brand and products (Taboola, Realize) across social platforms.
Manual monitoring is time-consuming and doesn't scale.

### Success Criteria
| Criteria | Target |
|----------|--------|
| **Data Quality** | >80% of ingested posts are genuinely about Taboola/Realize (validated by LLM) |
| **Field-Level Insights** | Sentiment classified into actionable categories (Pricing, Performance, Support, etc.) |
| **Reproducibility** | End-to-end pipeline, env vars for all secrets |
| **Freshness** | Supports on-demand refresh to fetch latest posts |
| **Usability** | Dashboard enables filtering by entity, platform, and topic. shows trends over time |


## Architecture

```
Reddit API + HN API → Data Ingestion → LLM Validation → Ranking → FastAPI → React Dashboard
```

## Model & prompt choices

### LLM Choice
- **Model**: GPT-4o-mini (fast, cost-effective)
- **Format**: JSON response format for structured output (ensure consistency)

### Entity
- **Taboola**: Unique name, low false-positive risk
- **Realize**: Two-phase approach (capitalized + context keywords like "advertising", "platform")

### Engagement Score
```
score = upvotes × 1.0 + comments × 2.0 + upvote_ratio × 10
```


## Limitations

- No persistence (in-memory cache only)
- Reddit API rate limits
- English only

## Next steps
- Add social website and platforms (LinkedIn. Facebook etc)
- Automation data extract each day
