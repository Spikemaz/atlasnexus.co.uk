"""
Market News Service for Securitisation Intelligence
Aggregates news from multiple financial sources
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

class MarketNewsService:
    def __init__(self):
        self.sources = {
            'ft': 'Financial Times',
            'citywire': 'City Wire',
            'greenst': 'Green Street News',
            'propweek': 'Property Week',
            'benews': 'BE News',
            'bloomberg': 'Bloomberg',
            'reuters': 'Reuters',
            'wsj': 'Wall Street Journal',
            'euromoney': 'Euromoney',
            'risk': 'Risk Magazine'
        }
        
        self.asset_classes = ['RMBS', 'CMBS', 'ABS', 'CLO', 'CDO', 'MBS', 'CRE CLO']
        self.regions = ['UK', 'EU', 'USA', 'Asia Pacific', 'Global']
        
    def generate_sample_news(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate sample news articles for demonstration"""
        news_templates = [
            {
                'type': 'BREAKING',
                'titles': [
                    '{region} {asset} Market Sees Record Issuance of {amount}',
                    'Major Bank Announces {amount} {asset} Programme in {region}',
                    '{region} Regulators Approve New {asset} Framework',
                    'Surprise Rate Cut Impacts {region} {asset} Spreads'
                ]
            },
            {
                'type': 'MARKET MOVE',
                'titles': [
                    '{asset} Spreads Tighten {bps}bps on Strong Demand',
                    '{region} {asset} Market Rallies on Economic Data',
                    'Investors Flock to {asset} Amid Market Volatility',
                    '{asset} Pricing Improves in {region} Secondary Market'
                ]
            },
            {
                'type': 'ANALYSIS',
                'titles': [
                    'Deep Dive: Why {region} {asset} Outperforms Peers',
                    'Market Outlook: {asset} Trends for 2024',
                    'Expert View: {region} Securitisation Market Analysis',
                    'Research: Impact of Basel IV on {asset} Markets'
                ]
            },
            {
                'type': 'DEAL NEWS',
                'titles': [
                    '{amount} {asset} Deal Prices Successfully in {region}',
                    'Landmark {asset} Transaction Closes in {region}',
                    'Innovative {asset} Structure Debuts in {region} Market',
                    'Record-Breaking {asset} Deal Announced for {region}'
                ]
            },
            {
                'type': 'REGULATORY',
                'titles': [
                    '{region} Updates {asset} Regulatory Requirements',
                    'New ESG Guidelines for {asset} Market',
                    '{region} Central Bank Reviews {asset} Risk Weights',
                    'Regulatory Changes Impact {asset} Issuance'
                ]
            }
        ]
        
        news_items = []
        current_time = datetime.now()
        
        for i in range(count):
            template_group = random.choice(news_templates)
            title_template = random.choice(template_group['titles'])
            
            # Generate random values
            region = random.choice(self.regions)
            asset = random.choice(self.asset_classes)
            amount = f"€{random.randint(100, 5000):,}M"
            bps = random.randint(5, 50)
            source_key = random.choice(list(self.sources.keys()))
            
            # Calculate time ago
            minutes_ago = random.randint(1, 1440)  # Up to 24 hours
            post_time = current_time - timedelta(minutes=minutes_ago)
            
            if minutes_ago < 60:
                time_str = f"{minutes_ago} minute{'s' if minutes_ago != 1 else ''} ago"
            elif minutes_ago < 1440:
                hours = minutes_ago // 60
                time_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                time_str = "Yesterday"
            
            # Generate title and content
            title = title_template.format(
                region=region,
                asset=asset,
                amount=amount,
                bps=bps
            )
            
            content = self.generate_content(title, region, asset)
            
            news_items.append({
                'id': f'news_{i}',
                'type': template_group['type'],
                'title': title,
                'content': content,
                'source': self.sources[source_key],
                'source_key': source_key,
                'time': time_str,
                'timestamp': post_time.isoformat(),
                'region': region,
                'asset_class': asset,
                'tags': self.generate_tags(region, asset, template_group['type']),
                'sentiment': random.choice(['positive', 'neutral', 'negative']),
                'impact': random.choice(['high', 'medium', 'low'])
            })
        
        # Sort by timestamp (most recent first)
        news_items.sort(key=lambda x: x['timestamp'], reverse=True)
        return news_items
    
    def generate_content(self, title: str, region: str, asset: str) -> str:
        """Generate article content based on title"""
        content_templates = [
            f"Market participants report strong demand for {asset} securities in the {region} market, with recent transactions significantly oversubscribed. Analysts attribute this to improving economic fundamentals and attractive relative value...",
            f"The {region} securitisation market continues to evolve with new {asset} structures gaining traction among institutional investors. Market observers note the importance of these developments for long-term market growth...",
            f"Recent data shows {asset} performance in {region} exceeding expectations, with delinquency rates remaining below historical averages. This positive trend has encouraged new issuers to enter the market...",
            f"Investment managers are increasingly focusing on {region} {asset} opportunities as spreads offer attractive risk-adjusted returns. The sector has shown resilience despite broader market volatility...",
            f"Regulatory developments in {region} are shaping the future of {asset} markets, with new guidelines aimed at enhancing transparency and investor protection. Market participants are adapting to these changes..."
        ]
        return random.choice(content_templates)
    
    def generate_tags(self, region: str, asset: str, news_type: str) -> List[str]:
        """Generate relevant tags for news item"""
        tags = [region, asset]
        
        type_tags = {
            'BREAKING': ['Market Alert', 'Breaking News'],
            'MARKET MOVE': ['Market Update', 'Spreads', 'Trading'],
            'ANALYSIS': ['Research', 'Market Analysis', 'Insights'],
            'DEAL NEWS': ['New Issue', 'Primary Market', 'Transactions'],
            'REGULATORY': ['Regulation', 'Compliance', 'Policy']
        }
        
        tags.extend(type_tags.get(news_type, []))
        
        # Add random additional tags
        additional_tags = ['ESG', 'Green Bonds', 'STS', 'Risk Retention', 'Credit', 
                          'Yield', 'Liquidity', 'Innovation', 'Technology', 'Digital']
        tags.extend(random.sample(additional_tags, k=random.randint(1, 3)))
        
        return tags[:5]  # Limit to 5 tags
    
    def get_market_indicators(self) -> Dict[str, Any]:
        """Get current market indicators"""
        return {
            'sentiment': random.choice(['BULLISH', 'NEUTRAL', 'BEARISH']),
            'sentiment_score': random.randint(40, 80),
            'issuance_24h': f"€{random.uniform(2, 8):.1f}B",
            'issuance_trend': random.choice(['up', 'down', 'stable']),
            'active_deals': random.randint(100, 200),
            'avg_spread_change': random.randint(-20, 20),
            'indicators': {
                'LIBOR_3M': {
                    'value': f"{random.uniform(5.2, 5.4):.2f}%",
                    'change': random.choice(['up', 'down']),
                    'progress': random.randint(60, 90)
                },
                'SOFR': {
                    'value': f"{random.uniform(5.1, 5.3):.2f}%",
                    'change': random.choice(['up', 'down']),
                    'progress': random.randint(60, 85)
                },
                'EURIBOR_6M': {
                    'value': f"{random.uniform(3.8, 4.0):.2f}%",
                    'change': 'stable',
                    'progress': random.randint(50, 70)
                },
                'SONIA': {
                    'value': f"{random.uniform(5.1, 5.3):.2f}%",
                    'change': random.choice(['up', 'down']),
                    'progress': random.randint(65, 85)
                }
            }
        }
    
    def get_regional_data(self) -> List[Dict[str, Any]]:
        """Get regional market data"""
        return [
            {
                'region': 'United Kingdom',
                'flag': 'gb',
                'primary_asset': 'RMBS',
                'issuance': f"£{random.uniform(1.5, 3.0):.1f}B",
                'issuance_trend': random.choice(['up', 'down']),
                'avg_spread': f"+{random.randint(75, 95)}bps",
                'market_trend': random.choice(['Stable', 'Volatile', 'Tightening'])
            },
            {
                'region': 'European Union',
                'flag': 'eu',
                'primary_asset': 'ABS',
                'issuance': f"€{random.uniform(2.5, 4.0):.1f}B",
                'issuance_trend': random.choice(['up', 'down']),
                'avg_spread': f"+{random.randint(85, 110)}bps",
                'market_trend': random.choice(['Stable', 'Volatile', 'Tightening'])
            },
            {
                'region': 'United States',
                'flag': 'us',
                'primary_asset': 'CLO',
                'issuance': f"${random.uniform(3.5, 6.0):.1f}B",
                'issuance_trend': random.choice(['up', 'down']),
                'avg_spread': f"+{random.randint(100, 130)}bps",
                'market_trend': random.choice(['Stable', 'Volatile', 'Tightening'])
            }
        ]
    
    def get_trending_topics(self) -> List[Dict[str, Any]]:
        """Get trending topics in securitisation"""
        topics = [
            'Green Securitisation',
            'ESG Compliance',
            'Digital Assets ABS',
            'Basel IV Impact',
            'STS Criteria Updates',
            'LIBOR Transition',
            'Climate Risk',
            'NPL Securitisation',
            'Synthetic CLOs',
            'Blockchain in ABS'
        ]
        
        return [
            {'rank': i+1, 'topic': topic, 'mentions': random.randint(50, 500)}
            for i, topic in enumerate(random.sample(topics, k=5))
        ]
    
    def get_upcoming_events(self) -> List[Dict[str, Any]]:
        """Get upcoming market events"""
        events = [
            {
                'date': 'Tomorrow',
                'time': '09:00 GMT',
                'title': 'ECB Policy Meeting',
                'impact': 'High',
                'description': 'Expected to discuss securitisation framework updates'
            },
            {
                'date': 'Dec 15',
                'time': '14:30 EST',
                'title': 'Fed Rate Decision',
                'impact': 'Critical',
                'description': 'Market awaits guidance on 2024 monetary policy'
            },
            {
                'date': 'Dec 18',
                'time': 'All Day',
                'title': 'Q4 Issuance Deadline',
                'impact': 'Medium',
                'description': 'Final window for year-end transactions'
            },
            {
                'date': 'Dec 20',
                'time': '10:00 GMT',
                'title': 'Bank of England MPC',
                'impact': 'High',
                'description': 'UK monetary policy implications for RMBS market'
            },
            {
                'date': 'Jan 8',
                'time': '09:00 CET',
                'title': 'EU Securitisation Forum',
                'impact': 'Medium',
                'description': 'Annual conference on market developments'
            }
        ]
        return events[:3]  # Return top 3 events
    
    def get_market_commentary(self) -> List[Dict[str, Any]]:
        """Get expert market commentary"""
        experts = [
            {
                'name': 'John Smith',
                'title': 'Chief Market Strategist',
                'organization': 'Financial Times',
                'comment': 'The European securitisation market is showing remarkable resilience despite macroeconomic headwinds. We\'re seeing particularly strong demand for ESG-compliant structures, which could define the market direction for 2024.',
                'time': '2 hours ago'
            },
            {
                'name': 'Sarah Johnson',
                'title': 'Head of Research',
                'organization': 'City Wire',
                'comment': 'UK RMBS continues to outperform expectations. The recent housing data suggests we might see tighter spreads heading into Q1 2024, particularly for prime mortgage pools.',
                'time': '4 hours ago'
            },
            {
                'name': 'Michael Chen',
                'title': 'Senior Analyst',
                'organization': 'Bloomberg',
                'comment': 'US CLO market dynamics are shifting with the rise in interest rates. We\'re observing more selective investor behavior, focusing on higher-rated tranches and established managers.',
                'time': '6 hours ago'
            },
            {
                'name': 'Emma Williams',
                'title': 'Portfolio Manager',
                'organization': 'Green Street',
                'comment': 'Commercial real estate securitisation faces headwinds, but selective opportunities remain in logistics and residential sectors. Geographic diversification is key.',
                'time': '8 hours ago'
            }
        ]
        return random.sample(experts, k=2)