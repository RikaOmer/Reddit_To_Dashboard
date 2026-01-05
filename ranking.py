def calculate_post_score(post: dict) -> float:
    """Calculate engagement score from upvotes, comments, and quality."""
    return (
        post.get('score', 0) * 1.0 +
        post.get('num_comments', 0) * 2.0 +
        post.get('upvote_ratio', 0) * 10
    )


def get_category_distribution(posts: list) -> dict:
    """Calculate category distribution with sentiment breakdown."""
    if not posts:
        return {}
    
    categories = {}
    for post in posts:
        subject = post.get('validation', {}).get('subject', 'N/A')
        sentiment = post.get('validation', {}).get('sentiment', 'neutral').lower()
        
        if subject not in categories:
            categories[subject] = {'posts': [], 'sentiments': {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0}}
        
        categories[subject]['posts'].append(post)
        categories[subject]['sentiments'][sentiment] = categories[subject]['sentiments'].get(sentiment, 0) + 1
    
    # Build distribution with percentages
    total = len(posts)
    distribution = {}
    for category, data in categories.items():
        count = len(data['posts'])
        distribution[category] = {
            'percentage': round((count / total) * 100, 1),
            'count': count,
            'sentiment_breakdown': {k: round((v / count) * 100, 1) for k, v in data['sentiments'].items()}
        }
    
    return dict(sorted(distribution.items(), key=lambda x: x[1]['percentage'], reverse=True))


def get_top_scored_posts(posts: list, n: int = 10) -> list:
    """Return top N posts sorted by engagement score."""
    if not posts:
        return []
    
    scored = [{**p, 'engagement_score': calculate_post_score(p)} for p in posts]
    return sorted(scored, key=lambda x: x['engagement_score'], reverse=True)[:n]


def get_top_posts_by_category(posts: list, n_categories: int = 3, n_posts: int = 3) -> dict:
    """Get top posts from the top N categories."""
    if not posts:
        return {}
    
    distribution = get_category_distribution(posts)
    top_categories = list(distribution.keys())[:n_categories]
    
    posts_by_cat = {}
    for post in posts:
        subject = post.get('validation', {}).get('subject', 'N/A')
        if subject not in posts_by_cat:
            posts_by_cat[subject] = []
        posts_by_cat[subject].append(post)
    
    return {cat: get_top_scored_posts(posts_by_cat.get(cat, []), n_posts) for cat in top_categories if cat in posts_by_cat}


def rank_brand_posts(validated_results: dict) -> dict:
    """Main function: process validated results and generate rankings."""
    rankings = {}
    
    for brand, posts in validated_results.items():
        all_posts = [{**p, 'engagement_score': calculate_post_score(p)} for p in posts]
        
        rankings[brand] = {
            'total_posts': len(posts),
            'all_posts': all_posts,
            'category_distribution': get_category_distribution(posts),
            'top_posts': get_top_scored_posts(posts, n=10),
            'top_posts_by_category': get_top_posts_by_category(posts)
        }
    
    return rankings
