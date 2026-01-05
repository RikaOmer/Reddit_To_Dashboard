from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime

from redit_ingest import fetch_brand_mentions
from llm_validation import get_only_relevant_posts
from ranking import rank_brand_posts

app = FastAPI(title="Reddit Brand Dashboard API")

# Enable CORS for React frontend - must allow all origins for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Cache for the latest results
cached_data = {
    "rankings": None,
    "last_updated": None
}


@app.get("/")
def root():
    return {"status": "ok", "message": "Reddit Brand Dashboard API"}


@app.get("/api/rankings")
def get_rankings():
    """Get the current cached rankings data."""
    if cached_data["rankings"] is None:
        return {
            "success": False,
            "message": "No data available. Please refresh to fetch new data.",
            "data": None,
            "last_updated": None
        }
    
    return {
        "success": True,
        "data": cached_data["rankings"],
        "last_updated": cached_data["last_updated"]
    }


@app.post("/api/refresh")
def refresh_data():
    """Fetch fresh data from Reddit, validate, and rank."""
    try:
        print("📥 Fetching Reddit posts...")
        brands = ["Taboola", "Realize"]
        reddit_results = fetch_brand_mentions(brands, limit=30)
        
        print("\n🤖 Validating posts with OpenAI...")
        relevant_posts = get_only_relevant_posts(reddit_results)
        
        print("\n📊 Generating rankings...")
        rankings = rank_brand_posts(relevant_posts)
        
        # Store in cache
        cached_data["rankings"] = rankings
        cached_data["last_updated"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Data refreshed successfully",
            "data": rankings,
            "last_updated": cached_data["last_updated"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error refreshing data: {str(e)}",
            "data": None,
            "last_updated": None
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

