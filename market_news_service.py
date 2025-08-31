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
            
            # Generate unique article URL based on source and article ID
            article_slug = title.lower().replace(' ', '-').replace(',', '').replace('.', '')[:50]
            article_id = f"{random.randint(1000000, 9999999)}"
            
            external_urls = {
                'ft': f'https://www.ft.com/content/{article_id}',
                'citywire': f'https://citywire.com/wealth-manager/news/{article_slug}/{article_id}',
                'greenst': f'https://www.greenstreet.com/insights/{article_slug}',
                'propweek': f'https://www.propertyweek.com/news/{article_slug}/{article_id}',
                'benews': f'https://www.bebeez.it/en/{article_slug}/',
                'bloomberg': f'https://www.bloomberg.com/news/articles/2024-{post_time.month:02d}-{post_time.day:02d}/{article_slug}',
                'reuters': f'https://www.reuters.com/business/finance/2024-{post_time.month:02d}-{post_time.day:02d}/{article_slug}',
                'wsj': f'https://www.wsj.com/articles/{article_slug}-{article_id}',
                'euromoney': f'https://www.euromoney.com/article/{article_id}/{article_slug}',
                'risk': f'https://www.risk.net/derivatives/{article_id}/{article_slug}'
            }
            
            news_items.append({
                'id': f'news_{i}',
                'type': template_group['type'],
                'title': title,
                'content': content,
                'source': self.sources[source_key],
                'source_key': source_key,
                'external_url': external_urls.get(source_key, 'https://www.ft.com/capital-markets'),
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
    
    def get_market_commentary(self, page: int = 0, per_page: int = 2) -> Dict[str, Any]:
        """Get expert market commentary with pagination"""
        # Expanded pool of market experts
        experts = [
            {
                'id': 'john_smith',
                'name': 'John Smith',
                'title': 'Chief Market Strategist',
                'organization': 'Financial Times',
                'avatar_color': 'primary',
                'expertise': ['European Markets', 'ESG', 'RMBS'],
                'comment_count': 15,
                'comments': [
                    {
                        'text': 'The European securitisation market is showing remarkable resilience despite macroeconomic headwinds. We\'re seeing particularly strong demand for ESG-compliant structures, which could define the market direction for 2024.',
                        'time': '2 hours ago',
                        'likes': 234,
                        'topic': 'ESG Securitisation'
                    },
                    {
                        'text': 'Recent ECB guidance on green bond standards will accelerate the transformation of European ABS markets. Issuers need to prepare for stricter reporting requirements.',
                        'time': '1 day ago',
                        'likes': 189,
                        'topic': 'Regulatory Updates'
                    },
                    {
                        'text': 'German auto ABS showing signs of stress as EV transition impacts residual values. Traditional models need recalibration for the new automotive landscape.',
                        'time': '3 days ago',
                        'likes': 156,
                        'topic': 'Auto ABS'
                    }
                ]
            },
            {
                'id': 'sarah_johnson',
                'name': 'Sarah Johnson',
                'title': 'Head of Research',
                'organization': 'City Wire',
                'avatar_color': 'success',
                'expertise': ['UK Markets', 'RMBS', 'Housing'],
                'comment_count': 23,
                'comments': [
                    {
                        'text': 'UK RMBS continues to outperform expectations. The recent housing data suggests we might see tighter spreads heading into Q1 2024, particularly for prime mortgage pools.',
                        'time': '4 hours ago',
                        'likes': 312,
                        'topic': 'UK RMBS'
                    },
                    {
                        'text': 'Buy-to-let RMBS facing pressure from regulatory changes. Expect to see more conservative LTV ratios and stricter affordability assessments going forward.',
                        'time': '2 days ago',
                        'likes': 278,
                        'topic': 'BTL Market'
                    }
                ]
            },
            {
                'id': 'michael_chen',
                'name': 'Michael Chen',
                'title': 'Senior Analyst',
                'organization': 'Bloomberg',
                'avatar_color': 'warning',
                'expertise': ['US Markets', 'CLO', 'Leveraged Loans'],
                'comment_count': 8,
                'comments': [
                    {
                        'text': 'US CLO market dynamics are shifting with the rise in interest rates. We\'re observing more selective investor behavior, focusing on higher-rated tranches and established managers.',
                        'time': '6 hours ago',
                        'likes': 198,
                        'topic': 'US CLO'
                    }
                ]
            },
            {
                'id': 'emma_williams',
                'name': 'Emma Williams',
                'title': 'Portfolio Manager',
                'organization': 'Green Street',
                'avatar_color': 'info',
                'expertise': ['CMBS', 'Real Estate', 'REITs'],
                'comment_count': 5,
                'comments': [
                    {
                        'text': 'Commercial real estate securitisation faces headwinds, but selective opportunities remain in logistics and residential sectors. Geographic diversification is key.',
                        'time': '8 hours ago',
                        'likes': 167,
                        'topic': 'CMBS Outlook'
                    }
                ]
            },
            {
                'id': 'david_mueller',
                'name': 'David Müller',
                'title': 'Head of Structured Finance',
                'organization': 'Deutsche Bank',
                'avatar_color': 'danger',
                'expertise': ['European CLO', 'Corporate Credit', 'Basel IV'],
                'comment_count': 19,
                'comments': [
                    {
                        'text': 'European CLO issuance picking up despite volatility. Strong demand from Japanese investors providing crucial support to the primary market.',
                        'time': '3 hours ago',
                        'likes': 245,
                        'topic': 'European CLO'
                    },
                    {
                        'text': 'Basel IV implementation will fundamentally change the economics of securitisation. Banks need to reassess their originate-to-distribute strategies.',
                        'time': '1 day ago',
                        'likes': 298,
                        'topic': 'Regulation'
                    }
                ]
            },
            {
                'id': 'alexandra_petrov',
                'name': 'Alexandra Petrov',
                'title': 'Managing Director',
                'organization': 'JP Morgan',
                'avatar_color': 'purple',
                'expertise': ['Emerging Markets', 'Cross-border', 'FX Risk'],
                'comment_count': 11,
                'comments': [
                    {
                        'text': 'Emerging market ABS showing resilience despite dollar strength. Local currency structures gaining traction as investors seek yield.',
                        'time': '5 hours ago',
                        'likes': 156,
                        'topic': 'EM ABS'
                    }
                ]
            },
            {
                'id': 'james_wong',
                'name': 'James Wong',
                'title': 'Chief Risk Officer',
                'organization': 'HSBC',
                'avatar_color': 'teal',
                'expertise': ['Risk Management', 'Asia Pacific', 'Credit Analysis'],
                'comment_count': 7,
                'comments': [
                    {
                        'text': 'Asian securitisation markets entering new growth phase. Singapore and Hong Kong competing to become regional hubs for green securitisation.',
                        'time': '7 hours ago',
                        'likes': 189,
                        'topic': 'APAC Markets'
                    }
                ]
            },
            {
                'id': 'marie_dubois',
                'name': 'Marie Dubois',
                'title': 'Head of ESG Investing',
                'organization': 'BNP Paribas',
                'avatar_color': 'success',
                'expertise': ['ESG', 'Green Bonds', 'Sustainability'],
                'comment_count': 14,
                'comments': [
                    {
                        'text': 'Green securitisation volume doubled in 2023. Expect continued growth as regulatory incentives and investor demand align.',
                        'time': '9 hours ago',
                        'likes': 267,
                        'topic': 'Green Finance'
                    },
                    {
                        'text': 'Social bonds backed by affordable housing loans showing strong performance. This could be the next frontier in sustainable securitisation.',
                        'time': '2 days ago',
                        'likes': 223,
                        'topic': 'Social Bonds'
                    }
                ]
            },
            {
                'id': 'robert_taylor',
                'name': 'Robert Taylor',
                'title': 'Global Head of ABS',
                'organization': 'Goldman Sachs',
                'avatar_color': 'warning',
                'expertise': ['Technology', 'Fintech', 'Innovation'],
                'comment_count': 9,
                'comments': [
                    {
                        'text': 'Fintech lenders increasingly turning to securitisation for funding. Data-driven underwriting showing promising early results.',
                        'time': '10 hours ago',
                        'likes': 198,
                        'topic': 'Fintech ABS'
                    }
                ]
            },
            {
                'id': 'sophia_martinez',
                'name': 'Sophia Martinez',
                'title': 'Senior Credit Analyst',
                'organization': 'Moody\'s',
                'avatar_color': 'info',
                'expertise': ['Credit Rating', 'Methodology', 'Surveillance'],
                'comment_count': 6,
                'comments': [
                    {
                        'text': 'Rating methodology updates for RMBS reflecting post-pandemic performance data. Expect more conservative assumptions on recovery rates.',
                        'time': '11 hours ago',
                        'likes': 145,
                        'topic': 'Rating Updates'
                    }
                ]
            },
            {
                'id': 'thomas_anderson',
                'name': 'Thomas Anderson',
                'title': 'Head of Trading',
                'organization': 'Barclays Capital',
                'avatar_color': 'primary',
                'expertise': ['Secondary Markets', 'Trading', 'Liquidity'],
                'comment_count': 12,
                'comments': [
                    {
                        'text': 'Secondary market liquidity improving across most asset classes. Bid-ask spreads tightening as market confidence returns.',
                        'time': '1 hour ago',
                        'likes': 178,
                        'topic': 'Market Liquidity'
                    },
                    {
                        'text': 'Electronic trading platforms revolutionizing ABS secondary markets. Expect continued digitalization of trading infrastructure.',
                        'time': '1 day ago',
                        'likes': 156,
                        'topic': 'Trading Technology'
                    }
                ]
            },
            {
                'id': 'linda_chen',
                'name': 'Linda Chen',
                'title': 'Chief Investment Officer',
                'organization': 'PIMCO',
                'avatar_color': 'danger',
                'expertise': ['Portfolio Management', 'Asset Allocation', 'Strategy'],
                'comment_count': 16,
                'comments': [
                    {
                        'text': 'Structured credit offering attractive risk-adjusted returns in current environment. Focusing on seasoned deals with proven performance.',
                        'time': '12 hours ago',
                        'likes': 234,
                        'topic': 'Investment Strategy'
                    }
                ]
            }
        ]
        
        # Filter experts who have more than one comment for "View All" feature
        frequent_experts = [e for e in experts if e['comment_count'] > 1]
        
        # Calculate pagination
        total_experts = len(experts)
        start_idx = page * per_page
        end_idx = min(start_idx + per_page, total_experts)
        
        # Get current page of experts
        current_experts = experts[start_idx:end_idx]
        
        # For each expert, select their most recent comment
        for expert in current_experts:
            if expert['comments']:
                expert['latest_comment'] = expert['comments'][0]
            else:
                expert['latest_comment'] = {
                    'text': 'No recent comments available.',
                    'time': 'N/A',
                    'likes': 0,
                    'topic': 'General'
                }
        
        return {
            'experts': current_experts,
            'frequent_experts': frequent_experts,
            'page': page,
            'per_page': per_page,
            'total': total_experts,
            'has_more': end_idx < total_experts
        }
    
    def get_expert_history(self, expert_id: str) -> Dict[str, Any]:
        """Get full comment history for a specific expert"""
        # This would normally query a database
        # For demo purposes, we'll return expanded data for known experts
        expert_data = self.get_market_commentary(page=0, per_page=100)
        
        for expert in expert_data['experts']:
            if expert['id'] == expert_id:
                return {
                    'status': 'success',
                    'expert': expert,
                    'total_comments': expert['comment_count'],
                    'comments': expert.get('comments', [])
                }
        
        return {
            'status': 'error',
            'message': 'Expert not found'
        }
    
    def get_active_deals(self) -> List[Dict[str, Any]]:
        """Get detailed information about active securitization deals"""
        deals = []
        
        # Generate sample deals with comprehensive information
        deal_templates = [
            # European deals
            {
                'id': 'deal_001',
                'name': 'Sunrise RMBS 2024-1',
                'issuer': 'Sunrise Finance PLC',
                'lead_manager': 'Deutsche Bank',
                'co_managers': ['BNP Paribas', 'Commerzbank'],
                'asset_class': 'RMBS',
                'region': 'Germany',
                'currency': 'EUR',
                'total_size': 1250000000,
                'tranches': [
                    {'class': 'A', 'size': 1000000000, 'rating': 'AAA', 'coupon': 'E3M + 85bps', 'wal': '3.5 years'},
                    {'class': 'B', 'size': 150000000, 'rating': 'AA', 'coupon': 'E3M + 125bps', 'wal': '5.2 years'},
                    {'class': 'C', 'size': 100000000, 'rating': 'A', 'coupon': 'E3M + 200bps', 'wal': '7.1 years'}
                ],
                'pricing_date': '2024-01-15',
                'closing_date': '2024-01-22',
                'status': 'Priced',
                'collateral': 'Prime German residential mortgages',
                'originator': 'Sunrise Bank AG',
                'servicer': 'Sunrise Servicing GmbH',
                'pool_characteristics': {
                    'number_of_loans': 8543,
                    'average_loan_size': 146250,
                    'wtd_avg_ltv': 65.3,
                    'wtd_avg_seasoning': '24 months',
                    'geographic_concentration': 'Bavaria (35%), NRW (25%), Baden-Württemberg (20%)'
                },
                'legal_structure': 'True Sale',
                'listing': 'Luxembourg Stock Exchange',
                'subscription_level': '3.2x oversubscribed'
            },
            {
                'id': 'deal_002',
                'name': 'Thames Auto ABS 2024-A',
                'issuer': 'Thames Auto Finance Ltd',
                'lead_manager': 'Barclays',
                'co_managers': ['HSBC', 'Lloyds'],
                'asset_class': 'Auto ABS',
                'region': 'United Kingdom',
                'currency': 'GBP',
                'total_size': 850000000,
                'tranches': [
                    {'class': 'A1', 'size': 400000000, 'rating': 'AAA', 'coupon': 'SONIA + 75bps', 'wal': '1.8 years'},
                    {'class': 'A2', 'size': 300000000, 'rating': 'AAA', 'coupon': 'SONIA + 95bps', 'wal': '2.9 years'},
                    {'class': 'B', 'size': 150000000, 'rating': 'AA', 'coupon': 'SONIA + 145bps', 'wal': '3.5 years'}
                ],
                'pricing_date': '2024-01-18',
                'closing_date': '2024-01-25',
                'status': 'Marketing',
                'collateral': 'UK prime auto loans',
                'originator': 'Thames Motor Finance',
                'servicer': 'Thames Servicing UK',
                'pool_characteristics': {
                    'number_of_loans': 45231,
                    'average_loan_size': 18750,
                    'wtd_avg_ltv': 85.2,
                    'wtd_avg_seasoning': '12 months',
                    'new_vs_used': '65% new / 35% used'
                },
                'legal_structure': 'True Sale with substitution',
                'listing': 'London Stock Exchange',
                'subscription_level': 'Building book'
            },
            {
                'id': 'deal_003',
                'name': 'Liberty Street CLO 2024-1',
                'issuer': 'Liberty Street Capital LLC',
                'lead_manager': 'JP Morgan',
                'co_managers': ['Goldman Sachs', 'Morgan Stanley'],
                'asset_class': 'CLO',
                'region': 'United States',
                'currency': 'USD',
                'total_size': 500000000,
                'tranches': [
                    {'class': 'A', 'size': 350000000, 'rating': 'AAA', 'coupon': 'SOFR + 150bps', 'wal': '5.0 years'},
                    {'class': 'B', 'size': 75000000, 'rating': 'AA', 'coupon': 'SOFR + 200bps', 'wal': '7.5 years'},
                    {'class': 'C', 'size': 50000000, 'rating': 'A', 'coupon': 'SOFR + 275bps', 'wal': '8.5 years'},
                    {'class': 'D', 'size': 25000000, 'rating': 'BBB', 'coupon': 'SOFR + 425bps', 'wal': '9.0 years'}
                ],
                'pricing_date': '2024-01-20',
                'closing_date': '2024-01-27',
                'status': 'Priced',
                'collateral': 'Broadly syndicated leveraged loans',
                'manager': 'Liberty Capital Management',
                'pool_characteristics': {
                    'number_of_obligors': 225,
                    'average_spread': 'S+385bps',
                    'wtd_avg_rating': 'B2/B',
                    'largest_industry': 'Healthcare (12%)',
                    'diversity_score': 78
                },
                'legal_structure': 'Cayman Islands SPV',
                'reinvestment_period': '4 years',
                'subscription_level': '2.5x oversubscribed'
            },
            {
                'id': 'deal_004',
                'name': 'Meridian CMBS 2024-1',
                'issuer': 'Meridian Commercial Real Estate',
                'lead_manager': 'Credit Suisse',
                'co_managers': ['Wells Fargo', 'Citi'],
                'asset_class': 'CMBS',
                'region': 'United States',
                'currency': 'USD',
                'total_size': 1500000000,
                'tranches': [
                    {'class': 'A1', 'size': 800000000, 'rating': 'AAA', 'coupon': '4.85% fixed', 'wal': '5.2 years'},
                    {'class': 'A2', 'size': 400000000, 'rating': 'AAA', 'coupon': '5.10% fixed', 'wal': '7.8 years'},
                    {'class': 'B', 'size': 200000000, 'rating': 'AA', 'coupon': '5.45% fixed', 'wal': '9.1 years'},
                    {'class': 'C', 'size': 100000000, 'rating': 'A', 'coupon': '5.95% fixed', 'wal': '9.5 years'}
                ],
                'pricing_date': '2024-01-12',
                'closing_date': '2024-01-19',
                'status': 'Closed',
                'collateral': 'US commercial real estate loans',
                'originator': 'Meridian Bank',
                'special_servicer': 'Meridian Asset Management',
                'pool_characteristics': {
                    'number_of_loans': 48,
                    'average_loan_size': 31250000,
                    'property_types': 'Office (40%), Retail (25%), Industrial (20%), Multifamily (15%)',
                    'geographic_distribution': 'NY (25%), CA (20%), TX (15%), FL (10%)',
                    'wtd_avg_dscr': 1.45
                },
                'legal_structure': 'REMIC',
                'listing': 'NYSE',
                'subscription_level': '1.8x oversubscribed'
            },
            {
                'id': 'deal_005',
                'name': 'Emerald Card ABS 2024-1',
                'issuer': 'Emerald Card Funding',
                'lead_manager': 'Bank of America',
                'co_managers': ['RBC Capital', 'TD Securities'],
                'asset_class': 'Credit Card ABS',
                'region': 'United States',
                'currency': 'USD',
                'total_size': 750000000,
                'tranches': [
                    {'class': 'A', 'size': 600000000, 'rating': 'AAA', 'coupon': 'SOFR + 45bps', 'wal': '2.1 years'},
                    {'class': 'B', 'size': 100000000, 'rating': 'AA', 'coupon': 'SOFR + 85bps', 'wal': '2.8 years'},
                    {'class': 'C', 'size': 50000000, 'rating': 'A', 'coupon': 'SOFR + 135bps', 'wal': '3.2 years'}
                ],
                'pricing_date': '2024-01-22',
                'closing_date': '2024-01-29',
                'status': 'Marketing',
                'collateral': 'Prime credit card receivables',
                'originator': 'Emerald Bank',
                'servicer': 'Emerald Card Services',
                'pool_characteristics': {
                    'number_of_accounts': 850000,
                    'average_balance': 882,
                    'payment_rate': '28.5%',
                    'charge_off_rate': '2.1%',
                    'average_fico': 740
                },
                'legal_structure': 'Master Trust',
                'early_amortization_triggers': 'Yes',
                'subscription_level': 'Initial price talk'
            },
            {
                'id': 'deal_006',
                'name': 'Alpine SME CLO 2024-1',
                'issuer': 'Alpine Capital S.A.',
                'lead_manager': 'UniCredit',
                'co_managers': ['Intesa Sanpaolo', 'BNP Paribas'],
                'asset_class': 'SME CLO',
                'region': 'Italy',
                'currency': 'EUR',
                'total_size': 400000000,
                'tranches': [
                    {'class': 'A', 'size': 320000000, 'rating': 'AAA', 'coupon': 'E3M + 95bps', 'wal': '4.5 years'},
                    {'class': 'B', 'size': 50000000, 'rating': 'AA', 'coupon': 'E3M + 175bps', 'wal': '6.2 years'},
                    {'class': 'C', 'size': 30000000, 'rating': 'A', 'coupon': 'E3M + 300bps', 'wal': '7.5 years'}
                ],
                'pricing_date': '2024-01-16',
                'closing_date': '2024-01-23',
                'status': 'Priced',
                'collateral': 'Italian SME loans',
                'originator': 'Alpine Bank SpA',
                'servicer': 'Alpine Servicing',
                'pool_characteristics': {
                    'number_of_borrowers': 523,
                    'average_loan_size': 765000,
                    'wtd_avg_maturity': '5.5 years',
                    'industry_concentration': 'Manufacturing (35%), Services (30%), Retail (20%)',
                    'geographic_concentration': 'Northern Italy (65%), Central (25%), South (10%)'
                },
                'legal_structure': 'Italian SPV - Law 130/99',
                'guarantee': 'EIF guarantee on senior tranche',
                'subscription_level': '2.1x oversubscribed'
            }
        ]
        
        # Add more variety with different statuses and regions
        for i, template in enumerate(deal_templates):
            # Calculate days since pricing
            pricing_date = datetime.strptime(template['pricing_date'], '%Y-%m-%d')
            days_since = (datetime.now() - pricing_date).days
            
            # Update status based on timing
            if days_since < 3:
                template['status'] = 'Just Priced'
                template['status_color'] = 'success'
            elif days_since < 7:
                template['status'] = 'Recently Closed'
                template['status_color'] = 'info'
            elif template['status'] == 'Marketing':
                template['status_color'] = 'warning'
            else:
                template['status_color'] = 'primary'
            
            # Add performance metrics for closed deals
            if template['status'] in ['Closed', 'Recently Closed']:
                template['performance'] = {
                    'spread_tightening': random.randint(-15, -5),
                    'final_allocation': f"{random.randint(60, 95)}% institutional / {random.randint(5, 40)}% retail",
                    'geographic_distribution': f"Europe {random.randint(40, 60)}%, Asia {random.randint(20, 35)}%, US {random.randint(15, 30)}%"
                }
            
            deals.append(template)
        
        # Sort by pricing date (most recent first)
        deals.sort(key=lambda x: x['pricing_date'], reverse=True)
        
        return deals[:20]  # Return top 20 deals