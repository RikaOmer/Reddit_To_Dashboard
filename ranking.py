"""
Ranking module for Reddit brand monitoring.
Provides functions to score, categorize, and rank validated posts.
"""

from typing import Dict, List


def calculate_post_score(post: dict) -> float:
    """
    Calculate engagement score for a single post.
    
    Formula:
        post['score'] * 1.0 +           # Upvotes matter
        post['num_comments'] * 2.0 +    # Comments = higher engagement
        post['upvote_ratio'] * 10       # Quality signal
    
    Args:
        post: Dictionary containing post data with score, num_comments, upvote_ratio
    
    Returns:
        Calculated engagement score as float
    """
    upvotes = post.get('score', 0) * 1.0
    comments = post.get('num_comments', 0) * 2.0
    quality = post.get('upvote_ratio', 0) * 10
    
    return upvotes + comments + quality


def get_category_distribution(posts: list) -> dict:
    """
    For each subject category, return percentage of posts and sentiment breakdown.
    
    Args:
        posts: List of validated posts with 'validation' containing 'subject' and 'sentiment'
    
    Returns:
        Dictionary with category stats:
        {
            "Performance": {
                "percentage": 25.0,
                "count": 5,
                "sentiment_breakdown": {
                    "positive": 60.0,
                    "negative": 20.0,
                    "neutral": 20.0,
                    "mixed": 0.0
                }
            }
        }
    """
    if not posts:
        return {}
    
    total_posts = len(posts)
    
    # Group posts by category
    category_posts = {}
    for post in posts:
        validation = post.get('validation', {})
        subject = validation.get('subject', 'N/A')
        sentiment = validation.get('sentiment', 'neutral').lower()
        
        if subject not in category_posts:
            category_posts[subject] = {
                'posts': [],
                'sentiments': {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0}
            }
        
        category_posts[subject]['posts'].append(post)
        if sentiment in category_posts[subject]['sentiments']:
            category_posts[subject]['sentiments'][sentiment] += 1
        else:
            category_posts[subject]['sentiments']['neutral'] += 1
    
    # Calculate percentages
    distribution = {}
    for category, data in category_posts.items():
        count = len(data['posts'])
        category_percentage = (count / total_posts) * 100 if total_posts > 0 else 0
        
        # Calculate sentiment breakdown percentages within this category
        sentiment_breakdown = {}
        for sentiment, sentiment_count in data['sentiments'].items():
            sentiment_breakdown[sentiment] = (sentiment_count / count) * 100 if count > 0 else 0
        
        distribution[category] = {
            'percentage': round(category_percentage, 1),
            'count': count,
            'sentiment_breakdown': {k: round(v, 1) for k, v in sentiment_breakdown.items()}
        }
    
    # Sort by percentage descending
    distribution = dict(sorted(distribution.items(), key=lambda x: x[1]['percentage'], reverse=True))
    
    return distribution


def get_top_scored_posts(posts: list, n: int = 10) -> list:
    """
    Return top N posts sorted by calculated engagement score (descending).
    
    Args:
        posts: List of validated posts
        n: Number of top posts to return (default 10)
    
    Returns:
        List of top N posts with 'engagement_score' added to each
    """
    if not posts:
        return []
    
    # Add engagement score to each post
    scored_posts = []
    for post in posts:
        post_copy = post.copy()
        post_copy['engagement_score'] = calculate_post_score(post)
        scored_posts.append(post_copy)
    
    # Sort by engagement score descending
    scored_posts.sort(key=lambda x: x['engagement_score'], reverse=True)
    
    return scored_posts[:n]


def get_top_posts_by_top_categories(posts: list, n_categories: int = 3, n_posts: int = 3) -> dict:
    """
    Get top posts from the top N categories by percentage.
    
    Args:
        posts: List of validated posts
        n_categories: Number of top categories to consider (default 3)
        n_posts: Number of top posts per category (default 3)
    
    Returns:
        Dictionary mapping top categories to their top posts:
        {
            "Performance": [post1, post2, post3],
            "Pricing": [post1, post2, post3]
        }
    """
    if not posts:
        return {}
    
    # Get category distribution to find top categories
    distribution = get_category_distribution(posts)
    
    # Get top N categories by percentage (already sorted)
    top_categories = list(distribution.keys())[:n_categories]
    
    # Group posts by category
    posts_by_category = {}
    for post in posts:
        validation = post.get('validation', {})
        subject = validation.get('subject', 'N/A')
        
        if subject not in posts_by_category:
            posts_by_category[subject] = []
        posts_by_category[subject].append(post)
    
    # Get top posts for each top category
    result = {}
    for category in top_categories:
        if category in posts_by_category:
            category_posts = posts_by_category[category]
            result[category] = get_top_scored_posts(category_posts, n_posts)
    
    return result


def rank_brand_posts(validated_results: dict) -> dict:
    """
    Main orchestration function that processes validated results for each brand.
    
    Args:
        validated_results: Dictionary from get_only_relevant_posts()
            {
                "Taboola": [list of validated posts],
                "Realize": [list of validated posts]
            }
    
    Returns:
        Comprehensive ranking data per brand:
        {
            "Taboola": {
                "total_posts": 20,
                "category_distribution": {...},
                "top_posts": [...],
                "top_posts_by_category": {...}
            }
        }
    """
    rankings = {}
    
    for brand, posts in validated_results.items():
        rankings[brand] = {
            'total_posts': len(posts),
            'category_distribution': get_category_distribution(posts),
            'top_posts': get_top_scored_posts(posts, n=10),
            'top_posts_by_category': get_top_posts_by_top_categories(posts, n_categories=3, n_posts=3)
        }
    
    return rankings


def print_ranking_report(rankings: dict):
    """
    Print a formatted report of the ranking results.
    
    Args:
        rankings: Output from rank_brand_posts()
    """
    for brand, data in rankings.items():
        print(f"\n{'='*80}")
        print(f"  {brand.upper()} RANKING REPORT")
        print(f"{'='*80}")
        print(f"Total Validated Posts: {data['total_posts']}")
        
        # Category Distribution
        print(f"\n{'─'*40}")
        print("CATEGORY DISTRIBUTION")
        print(f"{'─'*40}")
        
        for category, stats in data['category_distribution'].items():
            print(f"\n  {category}:")
            print(f"    Posts: {stats['count']} ({stats['percentage']}% of total)")
            print(f"    Sentiment Breakdown:")
            sb = stats['sentiment_breakdown']
            print(f"      Positive: {sb.get('positive', 0)}%")
            print(f"      Negative: {sb.get('negative', 0)}%")
            print(f"      Neutral:  {sb.get('neutral', 0)}%")
            print(f"      Mixed:    {sb.get('mixed', 0)}%")
        
        # Top Scored Posts Overall
        print(f"\n{'─'*40}")
        print("TOP SCORED POSTS (Overall)")
        print(f"{'─'*40}")
        
        for i, post in enumerate(data['top_posts'][:5], 1):
            title = post.get('title', 'No title')[:60]
            score = post.get('engagement_score', 0)
            sentiment = post.get('validation', {}).get('sentiment', 'N/A')
            subject = post.get('validation', {}).get('subject', 'N/A')
            link = post.get('permalink', 'No link')
            print(f"\n  [{i}] Score: {score:.1f}")
            print(f"      Title: {title}...")
            print(f"      Category: {subject} | Sentiment: {sentiment}")
            print(f"      Link: {link}")
        
        # Top Posts by Top Categories
        print(f"\n{'─'*40}")
        print("TOP 3 POSTS FROM TOP 3 CATEGORIES")
        print(f"{'─'*40}")
        
        for category, cat_posts in data['top_posts_by_category'].items():
            print(f"\n  [{category}]")
            for j, post in enumerate(cat_posts, 1):
                title = post.get('title', 'No title')[:50]
                score = post.get('engagement_score', 0)
                sentiment = post.get('validation', {}).get('sentiment', 'N/A')
                link = post.get('permalink', 'No link')
                print(f"    {j}. [{score:.1f}] {title}... ({sentiment})")
                print(f"       Link: {link}")


if __name__ == "__main__":
    # Example usage with the full pipeline
    from redit_ingest import fetch_brand_mentions
    from llm_validation import get_only_relevant_posts
    
    print("Fetching Reddit posts...")
    brands = ["Taboola", "Realize"]
    reddit_results = fetch_brand_mentions(brands, limit=30)
    
    print("\nValidating posts with OpenAI...")
    relevant_posts = get_only_relevant_posts(reddit_results)
    
    print("\nGenerating rankings...")
    rankings = rank_brand_posts(relevant_posts)
    
    # Print the report
    print_ranking_report(rankings)

