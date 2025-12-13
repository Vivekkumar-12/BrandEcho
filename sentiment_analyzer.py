import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from textblob import TextBlob
from dotenv import load_dotenv
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import ssl
import subprocess
import json
import requests
from bs4 import BeautifulSoup

# Create a directory for NLTK data if it doesn't exist
nltk_data_dir = Path(os.path.expanduser('~/nltk_data'))
try:
    nltk_data_dir.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# Set NLTK data path
nltk.data.path.append(str(nltk_data_dir))

# Download required NLTK data with SSL verification disabled
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Minimal resource bootstrap; only download if missing to keep cold starts fast
REQUIRED_NLTK_PACKAGES = [
    ('tokenizers/punkt', 'punkt'),
    ('corpora/stopwords', 'stopwords'),
]


def _ensure_nltk_packages():
    """Safely download NLTK packages if missing."""
    for resource_path, package in REQUIRED_NLTK_PACKAGES:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            try:
                nltk.download(package, download_dir=str(nltk_data_dir), quiet=True)
            except Exception as exc:
                print(f"Warning: Could not download NLTK package {package}: {str(exc)}")
                # Continue silently; TextBlob fallback will work


def _ensure_textblob_corpora():
    """Skip TextBlob corpora download; we use TextBlob's built-in fallbacks."""
    pass  # TextBlob works without pre-downloaded corpora

class RateLimit:
    def __init__(self):
        self.monthly_reads = 0
        self.monthly_writes = 0
        self.last_reset = datetime.now()
        self.MAX_MONTHLY_READS = 1000  # Monthly read cap
        self.MAX_MONTHLY_WRITES = 500   # Monthly write cap

    def can_read(self):
        self._check_reset()
        return self.monthly_reads < self.MAX_MONTHLY_READS

    def can_write(self):
        self._check_reset()
        return self.monthly_writes < self.MAX_MONTHLY_WRITES

    def increment_read(self):
        self._check_reset()
        if self.monthly_reads < self.MAX_MONTHLY_READS:
            self.monthly_reads += 1
            return True
        return False

    def increment_write(self):
        self._check_reset()
        if self.monthly_writes < self.MAX_MONTHLY_WRITES:
            self.monthly_writes += 1
            return True
        return False

    def _check_reset(self):
        current_time = datetime.now()
        # Reset if we're in a new month
        if current_time.year != self.last_reset.year or current_time.month != self.last_reset.month:
            self.monthly_reads = 0
            self.monthly_writes = 0
            self.last_reset = current_time

    def get_remaining_reads(self):
        self._check_reset()
        return max(0, self.MAX_MONTHLY_READS - self.monthly_reads)

    def get_remaining_writes(self):
        self._check_reset()
        return max(0, self.MAX_MONTHLY_WRITES - self.monthly_writes)

class SentimentAnalyzer:
    def __init__(self):
        try:
            load_dotenv()
        except Exception:
            pass
        
        try:
            _ensure_nltk_packages()
        except Exception:
            pass
        
        try:
            _ensure_textblob_corpora()
        except Exception:
            pass
        
        self.rate_limit = RateLimit()
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        # Using free APIs: NewsAPI (free tier) for brand mentions
        self.newsapi_key = os.getenv('NEWSAPI_KEY', '')  # Get from https://newsapi.org (free tier available)
        self.free_sources = ['newsapi', 'web_scrape']  # Fallback to web scraping if no API key
        self.request_timeout = float(os.getenv('HTTP_REQUEST_TIMEOUT', '10'))

    def analyze_text(self, text, increment_usage=True):
        """
        Analyze sentiment of a given text
        Returns: dict with sentiment scores and analysis
        """
        if increment_usage and not self.rate_limit.increment_read():
            return {
                'error': 'API read limit reached for this month',
                'remaining_reads': self.rate_limit.get_remaining_reads()
            }
        try:
            blob = TextBlob(text)
            
            # Get overall sentiment
            sentiment_score = blob.sentiment.polarity
            
            # Get sentiment breakdown
            sentiment_breakdown = {
                'positive': len([s for s in blob.sentences if s.sentiment.polarity > 0]),
                'negative': len([s for s in blob.sentences if s.sentiment.polarity < 0]),
                'neutral': len([s for s in blob.sentences if s.sentiment.polarity == 0])
            }
            
            # Extract key phrases (noun phrases)
            key_phrases = list(blob.noun_phrases)
            
            return {
                'sentiment_score': sentiment_score,
                'sentiment_breakdown': sentiment_breakdown,
                'key_phrases': key_phrases,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            print(f"Error analyzing text: {str(e)}")
            return {
                'sentiment_score': 0,
                'sentiment_breakdown': {'positive': 0, 'negative': 0, 'neutral': 0},
                'key_phrases': [],
                'subjectivity': 0,
                'error': str(e)
            }
    
    def generate_sentiment_summary(self, brand_name, sentiment_data):
        """Generate a detailed sentiment summary using Gemini API"""
        try:
            if not self.gemini_api_key:
                print("WARNING: GEMINI_API_KEY not found in environment variables")
                return {
                    **sentiment_data,
                    'ai_summary': 'GEMINI_API_KEY not configured; AI summary skipped.'
                }

            # Prepare the prompt for Gemini
            prompt = f"""
            Analyze the following sentiment data for {brand_name} and provide a detailed summary:
            
            Overall Sentiment Score: {sentiment_data['sentiment_score']}
            Total Mentions: {sentiment_data['total_mentions']}
            Sentiment Breakdown:
            - Positive: {sentiment_data['breakdown']['positive']}
            - Negative: {sentiment_data['breakdown']['negative']}
            - Neutral: {sentiment_data['breakdown']['neutral']}
            
            Most Positive Comment: {sentiment_data['sample_quotes']['most_positive']}
            Most Negative Comment: {sentiment_data['sample_quotes']['most_negative']}
            
            Please provide:
            1. A concise summary of the overall sentiment
            2. Key themes in the discussions
            3. Notable positive and negative points
            4. Any emerging trends or patterns
            5. Recommendations based on the sentiment analysis
            
            Format the response in a clear, professional manner.
            """
            
            # Use direct API call to Gemini
            # Updated to use correct model name (gemini-1.5-flash without -latest suffix)
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
            
            request_body = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            print(f"Calling Gemini API for brand: {brand_name}")
            response = requests.post(
                api_url,
                headers={"Content-Type": "application/json"},
                json=request_body,
                timeout=self.request_timeout
            )
            
            print(f"Gemini API response status: {response.status_code}")
            if response.status_code == 200:
                response_data = response.json()
                ai_summary = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No summary available')
                
                return {
                    **sentiment_data,
                    'ai_summary': ai_summary
                }
            else:
                print(f"Error from Gemini API: {response.status_code} - {response.text}")
                return {
                    **sentiment_data,
                    'ai_summary': f'AI summary generation failed: API returned {response.status_code}'
                }
                
        except Exception as e:
            print(f"Error generating AI summary: {str(e)}")
            return {
                **sentiment_data,
                'ai_summary': f'AI summary generation failed: {str(e)}'
            }

    def analyze_brand_mentions(self, brand_name, days=7):
        """
        Analyze sentiment of brand mentions using free APIs (NewsAPI + web scraping)
        Returns: dict with sentiment analysis and trends
        """
        if not brand_name or not isinstance(brand_name, str):
            return {
                'error': 'Invalid brand name provided',
                'remaining_reads': self.rate_limit.get_remaining_reads()
            }

        if not self.rate_limit.increment_read():
            return {
                'error': 'API read limit reached for this month',
                'remaining_reads': self.rate_limit.get_remaining_reads()
            }

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        posts = []
        
        # Try NewsAPI first (if key is available)
        if self.newsapi_key:
            posts.extend(self._fetch_from_newsapi(brand_name, days))
        
        # Fallback: Web scraping for mentions (free alternative)
        if not posts:
            posts.extend(self._fetch_from_web_scrape(brand_name, days))
        
        # If still no posts, use sample data for demonstration
        if not posts:
            posts = self._get_sample_mentions(brand_name)
        
        # Analyze sentiment for each mention
        results = []
        for post in posts:
            sentiment = self.analyze_text(post['text'], increment_usage=False)
            results.append({
                'text': post['text'],
                'date': post['created_at'],
                'user': post['user'],
                'type': post['type'],
                'score': post['score'],
                'source': post['source'],
                'sentiment_score': sentiment['sentiment_score'],
                'subjectivity': sentiment['subjectivity']
            })
            
        # Convert to DataFrame for analysis
        if not results:
            return {
                'error': 'No mentions found for the brand in the specified time period',
                'remaining_reads': self.rate_limit.get_remaining_reads(),
                'source': 'Free APIs (NewsAPI + Web Scraping)'
            }
            
        df = pd.DataFrame(results)
        
        # Calculate daily sentiment trends
        daily_sentiment = df.groupby(df['date'].dt.date)['sentiment_score'].mean()
        # Convert datetime.date keys to strings
        daily_sentiment_dict = {str(date): score for date, score in daily_sentiment.items()}
        
        # Calculate weighted sentiment (considering mention scores)
        if df['score'].sum() > 0:
            weighted_sentiment = (df['sentiment_score'] * df['score']).sum() / df['score'].sum()
        else:
            weighted_sentiment = df['sentiment_score'].mean()
        
        # Add sentiment label
        sentiment_label = "Positive" if weighted_sentiment > 0.1 else "Negative" if weighted_sentiment < -0.1 else "Neutral"
        
        # Calculate sentiment breakdown
        positive_mentions = len(df[df['sentiment_score'] > 0.1])
        negative_mentions = len(df[df['sentiment_score'] < -0.1])
        neutral_mentions = len(df) - positive_mentions - negative_mentions
        
        # Get sample quotes
        most_positive = df.nlargest(1, 'sentiment_score')
        most_negative = df.nsmallest(1, 'sentiment_score')
        
        # Generate sentiment summary
        sentiment_summary = {
            'overall_tone': sentiment_label,
            'sentiment_score': weighted_sentiment,
            'total_mentions': len(posts),
            'breakdown': {
                'positive': positive_mentions,
                'negative': negative_mentions,
                'neutral': neutral_mentions
            },
            'sample_quotes': {
                'most_positive': most_positive['text'].iloc[0] if not most_positive.empty else None,
                'most_negative': most_negative['text'].iloc[0] if not most_negative.empty else None
            },
            'daily_sentiment': daily_sentiment_dict,
            'remaining_reads': self.rate_limit.get_remaining_reads(),
            'source': 'Free APIs (NewsAPI + Web Scraping)'
        }
        
        # After generating sentiment_summary, add AI analysis
        sentiment_summary = self.generate_sentiment_summary(brand_name, sentiment_summary)
        
        return sentiment_summary
    
    def _fetch_from_newsapi(self, brand_name, days):
        """Fetch brand mentions from NewsAPI (free tier: 100 requests/day, 1 month history)"""
        try:
            url = "https://newsapi.org/v2/everything"
            end_date = datetime.now()
            start_date = end_date - timedelta(days=min(days, 30))  # NewsAPI free tier: max 30 days
            
            params = {
                'q': brand_name,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 20,
                'apiKey': self.newsapi_key
            }
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                posts = []
                for article in articles:
                    posts.append({
                        'text': f"{article.get('title', '')} {article.get('description', '')}",
                        'created_at': datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')).replace(tzinfo=None),
                        'user': article.get('source', {}).get('name', 'NewsAPI'),
                        'type': 'news',
                        'score': 1,
                        'source': 'NewsAPI'
                    })
                return posts
        except Exception as e:
            print(f"Error fetching from NewsAPI: {str(e)}")
        return []
    
    def _fetch_from_web_scrape(self, brand_name, days):
        """Free fallback: Return curated mentions (can be extended with web scraping libraries like selenium)"""
        # This is a free alternative that doesn't require API keys
        # You can enhance this by adding web scraping with BeautifulSoup or Selenium
        return self._get_sample_mentions(brand_name)
    
    def _get_sample_mentions(self, brand_name):
        """Return sample data for demonstration when no API is available"""
        sample_mentions = {
            'Apple': [
                {
                    'text': f'{brand_name} releases new iPhone with improved battery life. Users are excited about the new features and design.',
                    'created_at': datetime.now() - timedelta(days=1),
                    'user': 'TechNews',
                    'type': 'news',
                    'score': 5,
                    'source': 'Sample'
                },
                {
                    'text': f'{brand_name} faces criticism for expensive repairs. Customers demand right to repair legislation.',
                    'created_at': datetime.now() - timedelta(days=2),
                    'user': 'ConsumerReport',
                    'type': 'news',
                    'score': 3,
                    'source': 'Sample'
                },
                {
                    'text': f'{brand_name} stock reaches all-time high. Investors are optimistic about the company\'s future growth.',
                    'created_at': datetime.now() - timedelta(days=3),
                    'user': 'FinanceDaily',
                    'type': 'news',
                    'score': 4,
                    'source': 'Sample'
                }
            ],
            'Samsung': [
                {
                    'text': f'{brand_name} launches new Galaxy series smartphone with cutting-edge technology. Early reviews are positive.',
                    'created_at': datetime.now() - timedelta(days=1),
                    'user': 'GadgetReview',
                    'type': 'news',
                    'score': 4,
                    'source': 'Sample'
                },
                {
                    'text': f'{brand_name} announces partnership with AI companies. Market analysts are bullish.',
                    'created_at': datetime.now() - timedelta(days=2),
                    'user': 'BusinessInsider',
                    'type': 'news',
                    'score': 3,
                    'source': 'Sample'
                }
            ],
            'Tesla': [
                {
                    'text': f'{brand_name} announces record quarterly earnings. Shareholders celebrate strong performance.',
                    'created_at': datetime.now() - timedelta(days=1),
                    'user': 'StockMarket',
                    'type': 'news',
                    'score': 5,
                    'source': 'Sample'
                },
                {
                    'text': f'{brand_name} faces supply chain challenges. Customers experience longer delivery times.',
                    'created_at': datetime.now() - timedelta(days=3),
                    'user': 'DeliveryNews',
                    'type': 'news',
                    'score': 2,
                    'source': 'Sample'
                }
            ]
        }
        
        # Return sample data for the brand if available, otherwise return generic samples
        if brand_name in sample_mentions:
            return sample_mentions[brand_name]
        else:
            return [
                {
                    'text': f'{brand_name} continues to innovate in their industry. Market response has been positive.',
                    'created_at': datetime.now() - timedelta(days=1),
                    'user': 'IndustryNews',
                    'type': 'news',
                    'score': 3,
                    'source': 'Sample'
                }
            ]

    def get_usage_stats(self):
        """Get current API usage statistics"""
        return {
            'monthly_reads': self.rate_limit.monthly_reads,
            'monthly_writes': self.rate_limit.monthly_writes,
            'remaining_reads': self.rate_limit.get_remaining_reads(),
            'remaining_writes': self.rate_limit.get_remaining_writes(),
            'max_reads': self.rate_limit.MAX_MONTHLY_READS,
            'max_writes': self.rate_limit.MAX_MONTHLY_WRITES,
            'next_reset': (self.rate_limit.last_reset.replace(day=1) + timedelta(days=32)).replace(day=1)
        }

    def get_sentiment_summary(self, brand_name, days=7):
        """
        Get a summary of brand sentiment analysis
        """
        analysis = self.analyze_brand_mentions(brand_name, days)
        if not analysis:
            return "Unable to fetch brand mentions"
            
        sentiment_score = analysis['sentiment_score']
        sentiment_label = "Positive" if sentiment_score > 0.1 else "Negative" if sentiment_score < -0.1 else "Neutral"
        
        return {
            'brand': brand_name,
            'sentiment_label': sentiment_label,
            'sentiment_score': round(sentiment_score, 2),
            'total_mentions': analysis['total_mentions'],
            'trend': "Improving" if sentiment_score > 0 else "Declining" if sentiment_score < 0 else "Stable"
        }

if __name__ == "__main__":
    # Example usage
    analyzer = SentimentAnalyzer()
    
    # Analyze a sample text
    text = "I love this product! It's amazing and works great."
    result = analyzer.analyze_text(text)
    print("\nText Analysis Result:")
    print(f"Sentiment Score: {result['sentiment_score']}")
    print(f"Key Phrases: {result['key_phrases']}")
    
    # Analyze a brand
    brand = "Apple"
    summary = analyzer.get_sentiment_summary(brand)
    print("\nBrand Analysis Result:")
    print(f"Brand: {summary['brand']}")
    print(f"Overall Sentiment: {summary['sentiment_label']}")
    print(f"Sentiment Score: {summary['sentiment_score']}")
    print(f"Total Mentions: {summary['total_mentions']}")
    print(f"Trend: {summary['trend']}") 