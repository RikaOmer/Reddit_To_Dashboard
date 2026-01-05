"""
Reddit Post Data Extractor Module

This module handles the extraction and transformation of Reddit post data
into a structured format for further processing and analysis.
"""

from datetime import datetime
from typing import Optional


def extract_post_data(post, sort_by: str) -> dict:
    """
    Extract structured data from a Reddit post.
    
    Args:
        post: PRAW Submission object containing the Reddit post data
        sort_by: The sort type used to find this post (e.g., 'new', 'hot', 'relevance')
    
    Returns:
        dict: Structured post data with the following fields:
            - source: Always 'reddit'
            - ingest_type: The sort method used
            - id: Unique post identifier
            - text: Combined title and selftext
            - title: Post title
            - selftext: Post body content
            - url: URL associated with the post
            - permalink: Full Reddit permalink
            - created_utc: ISO format timestamp
            - date: Human-readable date string
            - author: Username or '[deleted]'
            - score: Post score (upvotes - downvotes)
            - num_comments: Number of comments
            - subreddit: Subreddit name
            - upvote_ratio: Ratio of upvotes to total votes
    """
    dt_object = datetime.fromtimestamp(post.created_utc)
    
    return {
        "source": "reddit",
        "ingest_type": sort_by,
        "id": post.id,
        "text": f"{post.title} {post.selftext}".strip(),
        "title": post.title,
        "selftext": post.selftext,
        "url": post.url,
        "permalink": f"https://reddit.com{post.permalink}",
        "created_utc": dt_object.isoformat(),
        "date": dt_object.strftime('%Y-%m-%d %H:%M:%S'),
        "author": _get_author(post.author),
        "score": post.score,
        "num_comments": post.num_comments,
        "subreddit": str(post.subreddit),
        "upvote_ratio": post.upvote_ratio
    }


def _get_author(author: Optional[object]) -> str:
    """
    Safely extract author username from a PRAW Redditor object.
    
    Args:
        author: PRAW Redditor object or None if deleted
    
    Returns:
        str: Username string or '[deleted]' if author is None
    """
    return str(author) if author else "[deleted]"


def extract_multiple_posts(posts: list, sort_by: str) -> list[dict]:
    """
    Extract structured data from multiple Reddit posts.
    
    Args:
        posts: List of PRAW Submission objects
        sort_by: The sort type used to find these posts
    
    Returns:
        list[dict]: List of structured post data dictionaries
    """
    return [extract_post_data(post, sort_by) for post in posts]

