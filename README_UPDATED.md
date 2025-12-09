# Brand Sentiment Analyzer

This project analyzes brand sentiment using multiple **free APIs** and natural language processing techniques.

## Features
✅ Text sentiment analysis using TextBlob  
✅ Brand mention tracking (using free APIs)  
✅ Sentiment visualization and reporting  
✅ **No expensive API subscriptions required!**

## Free APIs Used
- **TextBlob**: Free NLP library for sentiment analysis
- **NewsAPI**: Free tier (100 requests/day, 1 month history) - Optional
- **Web Scraping**: Fallback method when API keys unavailable
- **Sample Data**: Built-in demo data for testing without APIs
- **Gemini API**: Free tier for AI-powered summaries (optional)

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create `.env` File (Optional)
Create a `.env` file with optional API keys. **The app works fully in demo mode without these!**

```
# Optional API keys - leave empty for demo mode
NEWSAPI_KEY=your_newsapi_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free NewsAPI key at: https://newsapi.org

### 3. Run the Application

**Text Analysis Only:**
```bash
python sentiment_analyzer.py
```

**Full Web App with UI:**
```bash
python server.py
```
Then open your browser to `http://localhost:5000`

## Usage

### Analyze Text
```python
from sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.analyze_text("I love this product! It's amazing!")

print(result['sentiment_score'])  # Returns: 0.8 (positive)
print(result['key_phrases'])      # Returns: ['product']
```

### Analyze Brand Mentions
```python
result = analyzer.analyze_brand_mentions("Apple", days=7)

print(result['overall_tone'])        # Returns: "Positive"
print(result['total_mentions'])      # Returns: count of mentions found
print(result['breakdown'])           # Returns: {positive: X, negative: Y, neutral: Z}
```

## Output Format
```python
{
    'sentiment_score': 0.5,  # -1 (negative) to 1 (positive)
    'sentiment_breakdown': {
        'positive': 3,
        'negative': 1,
        'neutral': 2
    },
    'key_phrases': ['Apple', 'innovation'],
    'subjectivity': 0.6,  # 0 (objective) to 1 (subjective)
    'overall_tone': 'Positive',
    'daily_sentiment': {'2024-12-09': 0.5},
    'source': 'Free APIs (NewsAPI + Web Scraping)'
}
```

## API Migration Summary

### Removed (Paid/Limited APIs)
- ❌ **Tweepy** (Twitter API - requires paid tier)
- ❌ **PRAW** (Reddit API - rate limited, credentials required)

### Added (Free Alternatives)
- ✅ **NewsAPI** (Free tier: 100 requests/day, 1 month history)
- ✅ **Sample Data** (Built-in demo data for testing)
- ✅ **Web Scraping** (BeautifulSoup ready for custom scraping)

## Works Without API Keys!

The app includes **sample data** for demonstration:
- **Apple**: iPhone releases, repairs, stock news
- **Samsung**: Galaxy launches, partnerships
- **Tesla**: Earnings reports, supply chain news
- **Generic**: Default sample for any brand

Perfect for testing and development!

## Error Handling
- Graceful fallback to sample data if API fails
- Clear error messages for debugging
- No crashes due to missing API keys

## Tech Stack
- **Backend**: Flask, Python 3
- **NLP**: TextBlob, NLTK, pandas
- **APIs**: NewsAPI (free), Gemini (free)
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Utilities**: BeautifulSoup, requests

## Dependencies
See `requirements.txt` for complete list:
- textblob
- pandas
- nltk
- flask & flask-cors
- beautifulsoup4
- requests
- python-dotenv

## License
MIT
