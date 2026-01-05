import praw
import os
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MIN_YEAR = 2020
MIN_TIMESTAMP = datetime(MIN_YEAR, 1, 1).timestamp()  # Jan 1, 2020

SUBREDDITS = ['advertising', 'marketing', 'PPC', 'adops', 'programmatic', 'digital_marketing', 'adtech', 'startups', 'technology', 'business']
REALIZE_KEYWORDS = ['platform', 'app', 'software', 'company', 'campaign', 'advertising', 'marketing', 'ppc', 'ad']


def get_reddit_client():
    """Initialize Reddit client."""
    try:
        return praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_SECRET_KEY"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )
    except Exception as e:
        print(f"❌ Reddit connection error: {e}")
        return None


def fetch_brand_mentions(brand_names: list, limit: int = 30) -> dict:
    """Fetch Reddit posts mentioning the specified brands."""
    reddit = get_reddit_client()
    if not reddit:
        return {}

    results = {brand: [] for brand in brand_names}
    seen_ids = set()

    for brand in brand_names:
        print(f"🔍 Searching Reddit for: {brand}...")
        
        for subreddit_name in SUBREDDITS:
            if len(results[brand]) >= limit:
                break
            
            try:
                subreddit = reddit.subreddit(subreddit_name)
                for sort_by in ['new', 'hot', 'relevance']:
                    for post in subreddit.search(f'"{brand}"', sort=sort_by, limit=limit, time_filter='all'):
                        if len(results[brand]) >= limit or post.id in seen_ids:
                            continue
                        
                        if _is_relevant_post(post, brand) and post.created_utc >= MIN_TIMESTAMP:
                            seen_ids.add(post.id)
                            results[brand].append(_extract_post_data(post, sort_by))
            except Exception:
                continue
        
        print(f"  ✅ Found {len(results[brand])} posts for {brand}")
    
    return results


def _is_relevant_post(post, brand: str) -> bool:
    """Check if post is relevant to the brand."""
    text = f"{post.title} {post.selftext}"
    
    if brand.lower() not in text.lower():
        return False
    
    if brand == "Realize":
        has_context = any(kw in text.lower() for kw in REALIZE_KEYWORDS)
        has_capitalized = bool(re.search(r'\bRealize\b', text))
        return has_context and has_capitalized
    
    return True


def _extract_post_data(post, sort_by: str) -> dict:
    """Extract structured data from a Reddit post."""
    dt = datetime.fromtimestamp(post.created_utc)
    return {
        "source": "reddit",
        "ingest_type": sort_by,
        "id": post.id,
        "text": f"{post.title} {post.selftext}",
        "title": post.title,
        "selftext": post.selftext,
        "url": post.url,
        "permalink": f"https://reddit.com{post.permalink}",
        "created_utc": dt.isoformat(),
        "date": dt.strftime('%Y-%m-%d %H:%M:%S'),
        "author": str(post.author) if post.author else "[deleted]",
        "score": post.score,
        "num_comments": post.num_comments,
        "subreddit": str(post.subreddit),
        "upvote_ratio": post.upvote_ratio
    }
