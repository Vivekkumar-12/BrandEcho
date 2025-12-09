# Quick Start Guide

## 🚀 Get Started in 2 Minutes

### Option 1: No API Keys Needed (Recommended for Testing)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run with sample data (no setup required!)
python sentiment_analyzer.py
```

**Output:**
```
Sentiment Score: 0.8
Key Phrases: ['product']
```

### Option 2: With Web Interface

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the Flask server
python server.py

# 3. Open in browser
# http://localhost:5000
```

### Option 3: With NewsAPI (Enhanced)

```bash
# 1. Get free API key at https://newsapi.org (1 minute signup)

# 2. Create .env file
echo "NEWSAPI_KEY=your_key_here" > .env

# 3. Run
python sentiment_analyzer.py
```

## 📊 Example Usage

### Analyze Text
```python
from sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Positive text
result = analyzer.analyze_text("I love this amazing product!")
print(result['sentiment_score'])  # Output: ~0.8 (positive)

# Negative text
result = analyzer.analyze_text("This is terrible and disappointing.")
print(result['sentiment_score'])  # Output: ~-0.7 (negative)

# Neutral text
result = analyzer.analyze_text("The product has 4 wheels.")
print(result['sentiment_score'])  # Output: ~0.0 (neutral)
```

### Analyze Brand Mentions
```python
# Get sentiment for a brand
result = analyzer.analyze_brand_mentions("Apple", days=7)

print(result['overall_tone'])      # "Positive"
print(result['total_mentions'])    # 3
print(result['breakdown'])         # {'positive': 2, 'negative': 1, 'neutral': 0}
print(result['source'])            # "Free APIs (NewsAPI + Web Scraping)"
```

### Get Sample Data (Demo Brands)
```python
# These work immediately without API keys:
apple = analyzer.analyze_brand_mentions("Apple")     # ✅ Has sample data
samsung = analyzer.analyze_brand_mentions("Samsung") # ✅ Has sample data
tesla = analyzer.analyze_brand_mentions("Tesla")     # ✅ Has sample data
google = analyzer.analyze_brand_mentions("Google")   # ✅ Generic sample
```

## 📋 File Structure

```
AI-Sentiment-Analyzer1/
├── sentiment_analyzer.py    # Core NLP engine (updated with free APIs)
├── server.py                # Flask web server
├── index.html               # Web UI
├── chatbot.js               # Frontend logic
├── requirements.txt         # Python dependencies (updated)
├── README.md                # Original documentation
├── README_UPDATED.md        # New free API documentation
└── MIGRATION_GUIDE.md       # Detailed migration info
```

## 🆓 Free APIs

### NewsAPI
- **Cost**: Free (100 req/day)
- **Setup**: Sign up at https://newsapi.org
- **Time**: 1 minute
- **Optional**: App works without it

### Sample Data
- **Cost**: Free
- **Setup**: None needed
- **Always available**: Yes
- **Brands**: Apple, Samsung, Tesla, + generic

## 🔧 Configuration

### Minimal Setup (.env)
```
# Optional - leave empty for demo mode
NEWSAPI_KEY=
GEMINI_API_KEY=
```

### Full Setup (.env)
```
NEWSAPI_KEY=your_newsapi_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## ❓ FAQ

**Q: Do I need API keys to run?**
A: No! Works with sample data immediately.

**Q: How do I get more mentions?**
A: Add your free NewsAPI key (https://newsapi.org)

**Q: Which brands have sample data?**
A: Apple, Samsung, Tesla. Any other brand gets generic sample.

**Q: What if NewsAPI fails?**
A: Falls back to sample data automatically.

**Q: Can I add web scraping?**
A: Yes! Extend `_fetch_from_web_scrape()` method in sentiment_analyzer.py

**Q: Is the web UI updated?**
A: Yes, all endpoints work exactly the same.

## 📈 Sentiment Scores

Values range from **-1** to **+1**:

```
-1.0 -------- 0.0 -------- +1.0
Negative    Neutral      Positive
(angry)     (factual)    (happy)
```

Breakdown:
- **> +0.1**: Positive mention
- **< -0.1**: Negative mention  
- **Between**: Neutral/mixed

## 🎯 Next Steps

1. **Test with sample data**
   ```bash
   python sentiment_analyzer.py
   ```

2. **Add NewsAPI key** (optional)
   - Visit https://newsapi.org
   - Sign up for free
   - Add key to `.env`

3. **Launch web interface**
   ```bash
   python server.py
   ```

4. **Customize for your brands**
   - Edit `_get_sample_mentions()` in sentiment_analyzer.py
   - Add new sample data
   - Deploy!

## 🐛 Troubleshooting

### "No mentions found"
- Check that your brand name is correct
- Try built-in brands: Apple, Samsung, Tesla
- Add NewsAPI key for real data

### "Error fetching from NewsAPI"
- Verify API key is correct
- Check daily limit (100 req/day)
- App falls back to sample data

### "NLTK data missing"
- First run downloads required data automatically
- Check internet connection
- Rerun the script

## 📞 Support

- Check `MIGRATION_GUIDE.md` for detailed changes
- See `README_UPDATED.md` for API documentation
- Review sample data in `_get_sample_mentions()` method

---

**Happy Sentiment Analyzing! 🎉**

No API subscriptions required. Ever.
