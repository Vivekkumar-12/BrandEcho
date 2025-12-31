# Brand Sentiment Analyzer

This project analyzes brand sentiment using multiple APIs and natural language processing techniques.

## Features
- Text sentiment analysis using TextBlob
- Social media sentiment analysis (Twitter)
- Brand mention tracking
- Sentiment visualization and reporting

## Setup
1. Install dependencies (Python 3.9+):
```bash
pip install -r api/requirements.txt
```

2. Create a `.env` file with your API keys (see `.env.example`):
```
# Reddit (used for data sourcing)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=sentiment_analyzer:v1.0.0 (by /u/your_username)
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# Google Gemini (optional, AI summaries)
GEMINI_API_KEY=your_gemini_api_key
```

Security note: `.env` is now ignored by Git via `.gitignore`. Do not commit secrets. Rotate any previously exposed keys.

3. Run the analyzer:
```bash
python sentiment_analyzer.py
```

## Usage
The sentiment analyzer can be used in two ways:
1. Analyze text directly:
```python
from sentiment_analyzer import SentimentAnalyzer
analyzer = SentimentAnalyzer()
result = analyzer.analyze_text("Your text here")
```

2. Analyze brand mentions on social media:
```python
result = analyzer.analyze_brand_mentions("brand_name", days=7)
```

## Output
The analyzer provides:
- Overall sentiment score (-1 to 1)
- Sentiment breakdown (positive, negative, neutral)
- Key phrases and topics
- Sentiment trends over time 