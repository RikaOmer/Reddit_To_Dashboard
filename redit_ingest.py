import praw
import os
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Constants
RELEVANT_SUBREDDITS = [
    'advertising', 'marketing', 'PPC', 'adops', 'programmatic',
    'digital_marketing', 'adtech', 'socialmediamarketing',
    'startups', 'technology', 'business'
]
REALIZE_CONTEXT_KEYWORDS = [
    "platform", "app", "software", "company", "campaign", 
    "advertising", "marketing", "ppc", "ad"
]
SORT_TYPES = ['new', 'hot', 'relevance']


def get_reddit_client():
    """Initialize the Reddit client."""
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_SECRET_KEY"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )
        print(f"✅ Connected to Reddit)")
        return reddit
    except Exception as e:
        print(f"❌ Error connecting to Reddit: {e}")
        return None


def fetch_brand_mentions(brand_names, limit=30):
    reddit = get_reddit_client()
    if not reddit:
        return {}

    results = {brand: [] for brand in brand_names}
    seen_ids = set()

    for brand in brand_names:
        print(f"🔍 Processing Brand: {brand}...")
        
        # For Realize, do two-phase search: first capitalized, then lowercase
        if brand == "Realize":
            # Phase 1: Search for capitalized "Realize"
            print(f"🔍 Phase 1: Searching for capitalized 'Realize'...")
            for subreddit_name in RELEVANT_SUBREDDITS:
                if len(results[brand]) >= limit:
                    break
                try:
                    subreddit = reddit.subreddit(subreddit_name)
                    for sort_by in SORT_TYPES:
                        _search_subreddit(subreddit, brand, sort_by, limit, results, seen_ids, require_capitalized=True)
                except Exception as e:
                    print(f"Error accessing subreddit {subreddit_name}: {e}")
            
            # Phase 2: If limit not reached, search for lowercase "realize"
            if len(results[brand]) < limit:
                print(f"🔍 Phase 2: Searching for lowercase 'realize' (found {len(results[brand])}/{limit} so far)...")
                for subreddit_name in RELEVANT_SUBREDDITS:
                    if len(results[brand]) >= limit:
                        break
                    try:
                        subreddit = reddit.subreddit(subreddit_name)
                        for sort_by in SORT_TYPES:
                            _search_subreddit(subreddit, brand, sort_by, limit, results, seen_ids, require_capitalized=False)
                    except Exception as e:
                        print(f"Error accessing subreddit {subreddit_name}: {e}")
        else:
            for subreddit_name in RELEVANT_SUBREDDITS:
                try:
                    subreddit = reddit.subreddit(subreddit_name)
                    for sort_by in SORT_TYPES:
                        _search_subreddit(subreddit, brand, sort_by, limit, results, seen_ids)
                except Exception as e:
                    print(f"Error accessing subreddit {subreddit_name}: {e}")
    
    return results


def _search_subreddit(subreddit, brand, sort_by, limit, results, seen_ids, require_capitalized=True):
    """Search a single subreddit for brand mentions."""
    try:
        search_results = subreddit.search(
            f'"{brand}"', 
            sort=sort_by, 
            limit=limit,
            time_filter='all'
        )
        
        for post in search_results:
            if len(results[brand]) >= limit:
                break
            if post.id in seen_ids:
                continue
            
            context_keywords = REALIZE_CONTEXT_KEYWORDS if brand == "Realize" else []
            if is_relevant_post(post, brand, context_keywords, require_capitalized):
                seen_ids.add(post.id)
                results[brand].append(extract_post_data(post, sort_by))
    except Exception as e:
        print(f"Error searching {subreddit} ({sort_by}): {e}")


def is_relevant_post(post, brand, context_keywords, require_capitalized=True):
    """Check if the post is relevant to the brand."""
    full_text = f"{post.title} {post.selftext}".lower()
    
    if brand.lower() not in full_text:
        return False
    
    if brand == "Realize":
        has_context = any(kw in full_text for kw in context_keywords)
        if require_capitalized:
            # Phase 1: Must have capitalized "Realize" + context keyword
            has_realize = re.search(r'\bRealize\b', f"{post.title} {post.selftext}")
        else:
            # Phase 2: Allow lowercase "realize" + context keyword
            has_realize = re.search(r'\brealize\b', f"{post.title} {post.selftext}")
        return has_realize and has_context
    
    elif brand == "Taboola":
        return "taboola" in full_text
    
    return False


def extract_post_data(post, sort_by):
    """Extract structured data from a Reddit post."""
    dt_object = datetime.fromtimestamp(post.created_utc)
    return {
        "source": "reddit",
        "ingest_type": sort_by,
        "id": post.id,
        "text": f"{post.title} {post.selftext}",
        "title": post.title,
        "selftext": post.selftext,
        "url": post.url,
        "permalink": f"https://reddit.com{post.permalink}",
        "created_utc": dt_object.isoformat(),
        "date": dt_object.strftime('%Y-%m-%d %H:%M:%S'),
        "author": str(post.author) if post.author else "[deleted]",
        "score": post.score,
        "num_comments": post.num_comments,
        "subreddit": str(post.subreddit),
        "upvote_ratio": post.upvote_ratio
    }


if __name__ == "__main__":
    brands = ["Taboola", "Realize"]
    split_results = fetch_brand_mentions(brands, limit=30)
    
    for brand, posts in split_results.items():
        print(f"\n{'='*20} {brand} ({len(posts)} posts) {'='*20}")
        posts.sort(key=lambda x: x['created_utc'], reverse=True)
        
        for p in posts:
            print(f"[{p['ingest_type'].upper()}] r/{p['subreddit']} | {p['date']} | Score: {p['score']}")
            print(f"Title: {p['title'][:60]}...")
            print("-" * 40)
            