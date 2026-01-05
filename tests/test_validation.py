"""Tests for ranking and validation logic."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ranking import calculate_post_score, get_category_distribution, get_top_scored_posts


class TestPostScoring:
    def test_score_with_all_fields(self):
        post = {'score': 100, 'num_comments': 50, 'upvote_ratio': 0.95}
        assert calculate_post_score(post) == 209.5  # 100 + 100 + 9.5

    def test_score_with_missing_fields(self):
        assert calculate_post_score({}) == 0.0

    def test_score_partial_fields(self):
        assert calculate_post_score({'score': 50, 'num_comments': 10}) == 70.0


class TestCategoryDistribution:
    def test_empty_posts(self):
        assert get_category_distribution([]) == {}

    def test_single_category(self):
        posts = [
            {'validation': {'subject': 'Performance', 'sentiment': 'positive'}},
            {'validation': {'subject': 'Performance', 'sentiment': 'negative'}},
        ]
        result = get_category_distribution(posts)
        assert result['Performance']['count'] == 2
        assert result['Performance']['percentage'] == 100.0

    def test_multiple_categories(self):
        posts = [
            {'validation': {'subject': 'Performance', 'sentiment': 'positive'}},
            {'validation': {'subject': 'Pricing', 'sentiment': 'negative'}},
        ]
        result = get_category_distribution(posts)
        assert len(result) == 2
        assert result['Performance']['percentage'] == 50.0


class TestTopScoredPosts:
    def test_empty_posts(self):
        assert get_top_scored_posts([]) == []

    def test_returns_sorted_by_score(self):
        posts = [
            {'score': 10, 'num_comments': 5, 'upvote_ratio': 0.8},
            {'score': 100, 'num_comments': 50, 'upvote_ratio': 0.95},
        ]
        result = get_top_scored_posts(posts, n=2)
        assert result[0]['engagement_score'] > result[1]['engagement_score']

    def test_preserves_original_data(self):
        posts = [{'id': 'abc', 'title': 'Test', 'score': 100, 'num_comments': 10, 'upvote_ratio': 0.9}]
        result = get_top_scored_posts(posts, n=1)
        assert result[0]['id'] == 'abc'
        assert 'engagement_score' in result[0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
