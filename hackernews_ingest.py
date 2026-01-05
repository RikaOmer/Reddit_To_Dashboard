import requests
from datetime import datetime

HN_API = "https://hn.algolia.com/api/v1/search"
MIN_YEAR = 2020
MIN_TIMESTAMP = int(datetime(MIN_YEAR, 1, 1).timestamp())  # Jan 1, 2020
REALIZE_KEYWORDS = ['advertising', 'marketing', 'ppc', 'ad', 'adtech', 'taboola', 'campaign']


def fetch_hackernews_mentions(brand_names: list, limit: int = 30) -> dict:
    """Fetch Hacker News posts mentioning the specified brands."""
    results = {brand: [] for brand in brand_names}
    seen_ids = set()
    
    for brand in brand_names:
        print(f"🔍 Searching Hacker News for: {brand}...")
        
        try:
            posts = _search_hn(brand, limit, seen_ids)
            
            for post in posts:
                if len(results[brand]) >= limit:
                    break
                
                if brand == "Realize" and not _is_relevant_realize(post):
                    continue
                
                results[brand].append(post)
                seen_ids.add(post['id'])
            
            print(f"  ✅ Found {len(results[brand])} posts for {brand}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return results


def _search_hn(query: str, limit: int, seen_ids: set) -> list:
    """Search Hacker News via Algolia API."""
    posts = []
    
    # Search stories
    for tag in ['story', 'comment']:
        try:
            response = requests.get(HN_API, params={
                'query': query,
                'tags': tag,
                'hitsPerPage': min(limit * 2, 100),
                'numericFilters': f'created_at_i>{MIN_TIMESTAMP}'
            }, timeout=10)
            response.raise_for_status()
            
            for hit in response.json().get('hits', []):
                if hit.get('objectID') not in seen_ids:
                    post = _extract_data(hit, tag)
                    if post:
                        posts.append(post)
        except requests.RequestException:
            continue
    
    return posts


def _extract_data(hit: dict, item_type: str) -> dict:
    """Extract and format data from HN API response."""
    try:
        created_at = hit.get('created_at')
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00')) if created_at else datetime.now()
        
        if item_type == 'story':
            title = hit.get('title', '')
            text = hit.get('story_text', '') or ''
        else:
            title = f"Comment on: {hit.get('story_title', '')[:80]}"
            text = hit.get('comment_text', '') or ''
        
        return {
            "source": "hackernews",
            "ingest_type": item_type,
            "id": hit.get('objectID', ''),
            "text": f"{title} {text}".strip(),
            "title": title,
            "selftext": text,
            "url": hit.get('url', '') or hit.get('story_url', ''),
            "permalink": f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
            "created_utc": dt.isoformat(),
            "date": dt.strftime('%Y-%m-%d %H:%M:%S'),
            "author": hit.get('author', '[unknown]'),
            "score": hit.get('points', 0) or 0,
            "num_comments": hit.get('num_comments', 0) or 0,
            "subreddit": "hackernews",
            "upvote_ratio": 1.0
        }
    except Exception:
        return None


def _is_relevant_realize(post: dict) -> bool:
    """Check if post is about Realize company (not the verb)."""
    text = post.get('text', '')
    has_context = any(kw in text.lower() for kw in REALIZE_KEYWORDS)
    has_capitalized = 'Realize' in text
    return has_context or has_capitalized
