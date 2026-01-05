import os
from openai import OpenAI
from dotenv import load_dotenv
from redit_ingest import fetch_brand_mentions

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Company descriptions for context
COMPANY_DESCRIPTIONS = {
    "Taboola": """Taboola is a public advertising technology company that provides 
    content discovery and native advertising platform. They specialize in content 
    recommendations, sponsored content, and programmatic advertising. They partner 
    with publishers to show 'recommended content' widgets.""",
    
    "Realize": """Realize is an advertising/marketing technology company or platform.
    The context should relate to advertising, marketing campaigns, PPC, ad tech, 
    or digital marketing software/platforms."""
}

# Subject categories for classification
SUBJECT_CATEGORIES = [
    "Pricing",           # Cost, fees, pricing models, ROI
    "Performance",       # Results, metrics, effectiveness, conversion rates
    "Support",           # Customer service, help, response time
    "Features",          # Product capabilities, functionality
    "Integration",       # API, compatibility, setup, implementation
    "User Experience",   # Ease of use, interface, dashboard
    "General Discussion", # General mentions, news, announcements
    "Complaints",        # Issues, problems, bugs
    "Recommendations"    # Suggestions, advice, tips
]


def validate_post_relevance(post: dict, brand: str) -> dict:
    """
    Use OpenAI to validate if a Reddit post is truly about the specified company,
    classify the subject being discussed, and determine sentiment.
    
    Args:
        post: Dictionary containing post data (title, selftext, etc.)
        brand: The brand name to validate against ("Taboola" or "Realize")
    
    Returns:
        Dictionary with validation results including subject and sentiment
    """
    company_context = COMPANY_DESCRIPTIONS.get(brand, "")
    subjects_list = ", ".join(SUBJECT_CATEGORIES)
    
    prompt = f"""Analyze this Reddit post and determine if it's genuinely about {brand} company.

Company Context:
{company_context}

Reddit Post:
Title: {post.get('title', '')}
Content: {post.get('selftext', '')[:1500]}
Subreddit: r/{post.get('subreddit', '')}

Instructions:
1. Determine if this post is actually discussing {brand} the company/platform
2. Consider false positives: 
   - For "Taboola": Could be confused with other similar-sounding names
   - For "Realize": The word "realize" is commonly used as a verb meaning "to understand" or "to achieve"
3. Look for context clues: advertising, marketing, platform, campaigns, native ads, content recommendations
4. If relevant, classify the main SUBJECT being discussed from these categories: {subjects_list}
5. Determine the overall SENTIMENT toward {brand} in this post

Respond in this exact JSON format:
{{
    "is_relevant": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of your decision",
    "detected_context": "What the post is actually about",
    "subject": "Main subject category (from the list above, or 'N/A' if not relevant)",
    "subject_details": "Brief description of specific topic within the subject",
    "sentiment": "positive/negative/neutral/mixed",
    "sentiment_score": -1.0 to 1.0 (where -1 is very negative, 0 is neutral, 1 is very positive),
    "sentiment_reasoning": "Brief explanation of why this sentiment was determined"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing text to determine if it references specific companies. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        result["post_id"] = post.get("id")
        result["post_title"] = post.get("title", "")[:100]
        result["brand"] = brand
        return result
        
    except Exception as e:
        return {
            "post_id": post.get("id"),
            "post_title": post.get("title", "")[:100],
            "brand": brand,
            "is_relevant": None,
            "confidence": 0.0,
            "reasoning": f"Error during validation: {str(e)}",
            "detected_context": "Error",
            "subject": "N/A",
            "subject_details": "N/A",
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "sentiment_reasoning": "Error during analysis"
        }


def validate_all_posts(results: dict) -> dict:
    """
    Validate all posts from the Reddit ingestion results.
    
    Args:
        results: Dictionary with brand names as keys and lists of posts as values
    
    Returns:
        Dictionary with validation results for each brand
    """
    validated_results = {}
    
    for brand, posts in results.items():
        print(f"\n🔍 Validating {len(posts)} posts for {brand}...")
        validated_results[brand] = {
            "total_posts": len(posts),
            "relevant_posts": [],
            "irrelevant_posts": [],
            "errors": []
        }
        
        for i, post in enumerate(posts):
            print(f"  Checking post {i+1}/{len(posts)}: {post.get('title', '')[:50]}...")
            
            validation = validate_post_relevance(post, brand)
            
            if validation.get("is_relevant") is None:
                validated_results[brand]["errors"].append(validation)
            elif validation.get("is_relevant"):
                validated_results[brand]["relevant_posts"].append({
                    **post,
                    "validation": validation
                })
            else:
                validated_results[brand]["irrelevant_posts"].append({
                    **post,
                    "validation": validation
                })
        
        # Print summary for this brand
        relevant_count = len(validated_results[brand]["relevant_posts"])
        irrelevant_count = len(validated_results[brand]["irrelevant_posts"])
        error_count = len(validated_results[brand]["errors"])
        
        print(f"\n  ✅ {brand} Summary:")
        print(f"     - Relevant: {relevant_count}")
        print(f"     - Irrelevant (false positives): {irrelevant_count}")
        print(f"     - Errors: {error_count}")
    
    return validated_results


def get_sentiment_emoji(sentiment: str) -> str:
    """Get emoji for sentiment."""
    emoji_map = {
        "positive": "😊",
        "negative": "😞",
        "neutral": "😐",
        "mixed": "🤔"
    }
    return emoji_map.get(sentiment.lower(), "❓")


def print_detailed_results(validated_results: dict):
    """Print detailed validation results with subject and sentiment."""
    for brand, data in validated_results.items():
        print(f"\n{'='*80}")
        print(f"📊 {brand} - Relevant Posts ({len(data['relevant_posts'])} found)")
        print(f"{'='*80}")
        
        for i, post in enumerate(data["relevant_posts"], 1):
            v = post["validation"]
            sentiment_emoji = get_sentiment_emoji(v.get('sentiment', 'neutral'))
            confidence = v.get('confidence', 0)
            
            print(f"\n  [{i}] {post['title'][:75]}")
            print(f"      📂 Subject: {v.get('subject', 'N/A')}")
            print(f"      🎯 Relevance Confidence: {confidence:.0%}")
            print(f"      {sentiment_emoji} Sentiment: {v.get('sentiment', 'N/A').upper()} (score: {v.get('sentiment_score', 0):.2f})")
        
        # Print subject distribution for relevant posts
        if data['relevant_posts']:
            print(f"\n  {'-'*40}")
            print(f"  📂 SUBJECT DISTRIBUTION:")
            subject_counts = {}
            for post in data['relevant_posts']:
                subject = post['validation'].get('subject', 'N/A')
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
            for subject, count in sorted(subject_counts.items(), key=lambda x: -x[1]):
                print(f"       {subject}: {count}")
        
        # Print sentiment distribution for relevant posts
        if data['relevant_posts']:
            print(f"\n  😊 SENTIMENT DISTRIBUTION:")
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0}
            total_score = 0
            for post in data['relevant_posts']:
                sentiment = post['validation'].get('sentiment', 'neutral').lower()
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                total_score += post['validation'].get('sentiment_score', 0)
            
            for sentiment, count in sentiment_counts.items():
                if count > 0:
                    emoji = get_sentiment_emoji(sentiment)
                    print(f"       {emoji} {sentiment.capitalize()}: {count}")
            
            avg_score = total_score / len(data['relevant_posts'])
            print(f"       📈 Average sentiment score: {avg_score:.2f}")


def get_only_relevant_posts(results: dict) -> dict:
    """
    Filter and return only the posts validated as relevant to the companies.
    
    Args:
        results: Raw results from fetch_brand_mentions()
    
    Returns:
        Dictionary with only validated relevant posts
    """
    validated = validate_all_posts(results)
    
    return {
        brand: data["relevant_posts"]
        for brand, data in validated.items()
    }


if __name__ == "__main__":
    # Fetch Reddit posts
    print("📥 Fetching Reddit posts...")
    brands = ["Taboola", "Realize"]
    reddit_results = fetch_brand_mentions(brands, limit=30)
    
    # Validate with OpenAI
    print("\n🤖 Starting OpenAI validation...")
    validated_results = validate_all_posts(reddit_results)
    
    # Print detailed results
    print_detailed_results(validated_results)
    
    # Final summary
    print(f"\n{'='*70}")
    print("📈 FINAL SUMMARY")
    print(f"{'='*70}")
    
    for brand, data in validated_results.items():
        total = data["total_posts"]
        relevant = len(data["relevant_posts"])
        accuracy = (relevant / total * 100) if total > 0 else 0
        
        print(f"\n🏢 {brand}:")
        print(f"  Total posts found: {total}")
        print(f"  Validated as relevant: {relevant}")
        print(f"  False positives filtered: {len(data['irrelevant_posts'])}")
        print(f"  Relevance rate: {accuracy:.1f}%")
        
        if data["relevant_posts"]:
            # Calculate sentiment summary
            sentiments = [p['validation'].get('sentiment', 'neutral').lower() for p in data['relevant_posts']]
            positive_pct = sentiments.count('positive') / len(sentiments) * 100
            negative_pct = sentiments.count('negative') / len(sentiments) * 100
            neutral_pct = sentiments.count('neutral') / len(sentiments) * 100
            
            avg_score = sum(p['validation'].get('sentiment_score', 0) for p in data['relevant_posts']) / len(data['relevant_posts'])
            
            print(f"\n  📊 Sentiment Overview:")
            print(f"     😊 Positive: {positive_pct:.0f}%")
            print(f"     😞 Negative: {negative_pct:.0f}%")
            print(f"     😐 Neutral: {neutral_pct:.0f}%")
            print(f"     📈 Avg Score: {avg_score:.2f} (-1 to 1)")
            
            # Top subjects
            subjects = {}
            for p in data['relevant_posts']:
                subj = p['validation'].get('subject', 'N/A')
                subjects[subj] = subjects.get(subj, 0) + 1
            
            top_subjects = sorted(subjects.items(), key=lambda x: -x[1])[:3]
            print(f"\n  📂 Top Subjects:")
            for subj, count in top_subjects:
                print(f"     {subj}: {count}")

