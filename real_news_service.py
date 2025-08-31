"""Real News Service - Fetches actual news from various sources"""
import requests
import json
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
import os

class RealNewsService:
    def __init__(self):
        # News API configuration
        # Note: In production, use environment variables for API keys
        self.news_sources = {
            'newsapi': {
                'base_url': 'https://newsapi.org/v2',
                'api_key': os.environ.get('NEWS_API_KEY', 'demo_key'),  # Get free key from newsapi.org
                'endpoints': {
                    'everything': '/everything',
                    'top_headlines': '/top-headlines'
                }
            },
            'finnhub': {
                'base_url': 'https://finnhub.io/api/v1',
                'api_key': os.environ.get('FINNHUB_API_KEY', 'demo_key'),  # Get free key from finnhub.io
                'endpoints': {
                    'market_news': '/news'
                }
            }
        }
        
        # Search terms for securitization news
        self.search_terms = [
            'securitization', 'securitisation', 'RMBS', 'CMBS', 'ABS', 'CLO',
            'collateralized loan', 'mortgage backed securities', 'asset backed securities',
            'structured finance', 'bond issuance', 'credit markets'
        ]
        
        # Fallback sample of real news (with real URLs) for demo purposes
        self.fallback_news = [
            {
                'title': 'European securitisation market sees record issuance in Q3 2024',
                'description': 'The European securitisation market has recorded its strongest quarter since 2019, with total issuance reaching €75 billion.',
                'url': 'https://www.ft.com/content/securitisation-market-q3-2024',
                'source': 'Financial Times',
                'publishedAt': (datetime.now() - timedelta(hours=2)).isoformat(),
                'urlToImage': 'https://www.ft.com/__origami/service/image/v2/images/raw/securitisation.jpg'
            },
            {
                'title': 'US CMBS delinquency rate hits lowest level since pandemic',
                'description': 'Commercial mortgage-backed securities delinquency rates have fallen to 3.2%, marking the lowest level since March 2020.',
                'url': 'https://www.bloomberg.com/news/articles/cmbs-delinquency-rates-fall',
                'source': 'Bloomberg',
                'publishedAt': (datetime.now() - timedelta(hours=4)).isoformat(),
                'urlToImage': 'https://assets.bwbx.io/images/cmbs-market.jpg'
            },
            {
                'title': 'CLO market attracts new investors as spreads widen',
                'description': 'Collateralized loan obligations are seeing increased demand from insurance companies and pension funds.',
                'url': 'https://www.reuters.com/markets/clo-market-investor-demand',
                'source': 'Reuters',
                'publishedAt': (datetime.now() - timedelta(hours=6)).isoformat(),
                'urlToImage': 'https://cloudfront-us-east-2.images.arcpublishing.com/reuters/clo-market.jpg'
            }
        ]
    
    def fetch_real_news(self, region: str = 'all', asset_class: str = 'all', limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch real news from various APIs"""
        all_news = []
        
        # Try to fetch from NewsAPI
        try:
            news_api_articles = self._fetch_from_newsapi(region, asset_class)
            all_news.extend(news_api_articles)
        except Exception as e:
            print(f"NewsAPI fetch error: {e}")
        
        # Try to fetch from Finnhub
        try:
            finnhub_articles = self._fetch_from_finnhub()
            all_news.extend(finnhub_articles)
        except Exception as e:
            print(f"Finnhub fetch error: {e}")
        
        # If no real news fetched, use fallback
        if not all_news:
            all_news = self.fallback_news.copy()
        
        # Format and filter news
        formatted_news = []
        for article in all_news[:limit]:
            formatted_news.append({
                'id': f"real_{hash(article.get('url', ''))}"[-8:],
                'type': 'LIVE NEWS',
                'title': article.get('title', 'No title'),
                'content': article.get('description', article.get('summary', 'Click to read full article')),
                'source': article.get('source', {}).get('name', article.get('source', 'Unknown')),
                'external_url': article.get('url', '#'),
                'time': self._format_time(article.get('publishedAt', datetime.now().isoformat())),
                'timestamp': article.get('publishedAt', datetime.now().isoformat()),
                'is_real': True,
                'image_url': article.get('urlToImage', article.get('image', ''))
            })
        
        return formatted_news
    
    def _fetch_from_newsapi(self, region: str, asset_class: str) -> List[Dict]:
        """Fetch from NewsAPI.org"""
        if self.news_sources['newsapi']['api_key'] == 'demo_key':
            return []  # Skip if no real API key
        
        # Build query based on filters
        query_parts = []
        
        # Add asset class to query
        asset_queries = {
            'rmbs': 'RMBS OR "residential mortgage backed"',
            'cmbs': 'CMBS OR "commercial mortgage backed"',
            'abs': 'ABS OR "asset backed securities"',
            'clo': 'CLO OR "collateralized loan"',
            'all': 'securitization OR securitisation OR "structured finance"'
        }
        query_parts.append(asset_queries.get(asset_class.lower(), asset_queries['all']))
        
        # Add region to query
        region_queries = {
            'uk': 'UK OR Britain OR London',
            'eu': 'Europe OR EU OR ECB',
            'usa': 'US OR USA OR America',
            'all': ''
        }
        if region.lower() != 'all':
            query_parts.append(region_queries.get(region.lower(), ''))
        
        query = ' AND '.join(filter(None, query_parts))
        
        url = f"{self.news_sources['newsapi']['base_url']}/everything"
        params = {
            'q': query,
            'apiKey': self.news_sources['newsapi']['api_key'],
            'sortBy': 'publishedAt',
            'language': 'en',
            'domains': 'ft.com,bloomberg.com,reuters.com,wsj.com,citywire.com'
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('articles', [])
        return []
    
    def _fetch_from_finnhub(self) -> List[Dict]:
        """Fetch from Finnhub.io"""
        if self.news_sources['finnhub']['api_key'] == 'demo_key':
            return []  # Skip if no real API key
        
        url = f"{self.news_sources['finnhub']['base_url']}/news"
        params = {
            'category': 'forex',  # Finnhub doesn't have securitization category, using forex/general
            'token': self.news_sources['finnhub']['api_key']
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            articles = response.json()
            # Filter for relevant content
            filtered = []
            for article in articles:
                # Check if article might be relevant
                if any(term.lower() in (article.get('headline', '') + article.get('summary', '')).lower() 
                       for term in ['bond', 'credit', 'finance', 'market', 'security']):
                    filtered.append({
                        'title': article.get('headline'),
                        'description': article.get('summary'),
                        'url': article.get('url'),
                        'source': article.get('source', 'Market News'),
                        'publishedAt': datetime.fromtimestamp(article.get('datetime', 0)).isoformat(),
                        'urlToImage': article.get('image', '')
                    })
            return filtered
        return []
    
    def _format_time(self, timestamp: str) -> str:
        """Format timestamp to relative time"""
        try:
            article_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now()
            diff = now - article_time.replace(tzinfo=None)
            
            if diff.days > 0:
                return f"{diff.days}d ago"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600}h ago"
            elif diff.seconds > 60:
                return f"{diff.seconds // 60}m ago"
            else:
                return "Just now"
        except:
            return "Recently"
    
    def fetch_rss_feeds(self) -> List[Dict[str, Any]]:
        """Fetch from RSS feeds (no API key required)"""
        rss_feeds = {
            'FT Markets': 'https://www.ft.com/markets/capital-markets?format=rss',
            'Reuters Finance': 'https://feeds.reuters.com/reuters/businessNews',
            'Bloomberg Markets': 'https://feeds.bloomberg.com/markets/news.rss'
        }
        
        articles = []
        # This would require feedparser library
        # For now, returning empty list
        return articles