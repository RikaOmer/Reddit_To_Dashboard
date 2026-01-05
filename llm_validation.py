import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

COMPANY_DESCRIPTIONS = {
    "Taboola": "Taboola is a public advertising technology company that provides content discovery and native advertising platform.",
    "Realize": "Realize is Taboola's performance advertising platform for PPC/CPC campaigns.."
}

SUBJECT_CATEGORIES = [
    "Pricing", "Performance", "Support", "Features", "Integration","Career & Jobs",
    "User Experience", "Campaign Strategy", "Company News", "Complaints", "Recommendations"
]


def validate_post_relevance(post: dict, brand: str) -> dict:
    """Use OpenAI to validate if a post is about the specified company and analyze sentiment."""
    prompt = f"""Analyze this post and determine if it's genuinely about {brand} company.

Company Context: {COMPANY_DESCRIPTIONS.get(brand, "")}

Post:
Title: {post.get('title', '')}
Content: {post.get('selftext', '')[:1500]}
Subreddit: r/{post.get('subreddit', '')}

Instructions:
1. Determine if this post is about {brand} the company/platform
2. For "Realize": The word is commonly used as a verb - look for advertising/marketing context
3. If relevant, classify the SUBJECT from: {", ".join(SUBJECT_CATEGORIES)}
4. Determine SENTIMENT toward {brand}

Respond in JSON:
{{"is_relevant": true/false, "confidence": 0.0-1.0, "subject": "Category or N/A", "sentiment": "positive/negative/neutral", "sentiment_score": -1.0 to 1.0}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You analyze text to determine if it references specific companies. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        result["post_id"] = post.get("id")
        result["brand"] = brand
        return result
        
    except Exception:
        return {
            "post_id": post.get("id"),
            "brand": brand,
            "is_relevant": None,
            "confidence": 0.0,
            "subject": "N/A",
            "sentiment": "neutral",
            "sentiment_score": 0.0
        }


def get_only_relevant_posts(results: dict) -> dict:
    """Filter and return only posts validated as relevant to the companies."""
    validated = {}
    
    for brand, posts in results.items():
        print(f"🔍 Validating {len(posts)} posts for {brand}...")
        relevant = []
        
        for i, post in enumerate(posts):
            print(f"  [{i+1}/{len(posts)}] {post.get('title', '')[:50]}...")
            validation = validate_post_relevance(post, brand)
            
            if validation.get("is_relevant"):
                relevant.append({**post, "validation": validation})
        
        validated[brand] = relevant
        print(f"  ✅ {brand}: {len(relevant)} relevant posts")
    
    return validated
