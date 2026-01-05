from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from datetime import datetime

from reddit_ingest import fetch_brand_mentions
from hackernews_ingest import fetch_hackernews_mentions
from llm_validation import get_only_relevant_posts
from ranking import rank_brand_posts

app = FastAPI(title="Reddit Brand Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://localhost:5173"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

cached_data = {"rankings": None, "last_updated": None}


@app.get("/")
def root():
    return {"status": "ok", "message": "Reddit Brand Dashboard API"}


@app.get("/api/rankings")
def get_rankings():
    """Get cached rankings data."""
    if not cached_data["rankings"]:
        return {"success": False, "message": "No data. Click refresh to fetch.", "data": None}
    return {"success": True, "data": cached_data["rankings"], "last_updated": cached_data["last_updated"]}


@app.post("/api/refresh")
def refresh_data():
    """Fetch fresh data from Reddit/HN, validate with AI, and rank."""
    try:
        brands = ["Taboola", "Realize"]
        
        print("📥 Fetching Reddit posts...")
        reddit_results = fetch_brand_mentions(brands, limit=20)
        
        print("\n📥 Fetching Hacker News posts...")
        hn_results = fetch_hackernews_mentions(brands, limit=10)
        
        # Merge sources
        merged = {brand: reddit_results.get(brand, []) + hn_results.get(brand, []) for brand in brands}
        
        print("\n🤖 Validating with AI...")
        relevant = get_only_relevant_posts(merged)
        
        print("\n📊 Generating rankings...")
        rankings = rank_brand_posts(relevant)
        
        _save_output(relevant, rankings)
        
        cached_data["rankings"] = rankings
        cached_data["last_updated"] = datetime.now().isoformat()
        
        return {"success": True, "data": rankings, "last_updated": cached_data["last_updated"]}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e), "data": None}


def _save_output(relevant_posts: dict, rankings: dict):
    """Save output files for submission."""
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "items.jsonl"), 'w', encoding='utf-8') as f:
        for brand, posts in relevant_posts.items():
            for post in posts:
                f.write(json.dumps({**post, "brand": brand}, ensure_ascii=False) + "\n")
    
    with open(os.path.join(output_dir, "aggregates.json"), 'w', encoding='utf-8') as f:
        json.dump(rankings, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
