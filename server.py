from flask import Flask, request, jsonify, send_from_directory
from sentiment_analyzer import SentimentAnalyzer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize the sentiment analyzer
try:
    analyzer = SentimentAnalyzer()
except Exception as e:
    print(f"[WARNING] Failed to initialize SentimentAnalyzer: {str(e)}")
    import traceback
    traceback.print_exc()
    analyzer = None

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/analyze', methods=['POST'])
def analyze():
    if not analyzer:
        return jsonify({'error': 'Analyzer not initialized'}), 500
        
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Analyze the text
        result = analyzer.analyze_text(text)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"[ERROR] /analyze: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-brand', methods=['POST'])
def analyze_brand():
    if not analyzer:
        return jsonify({'error': 'Analyzer not initialized'}), 500
        
    data = request.json
    brand = data.get('brand', '')
    days = data.get('days', 7)
    
    if not brand:
        return jsonify({'error': 'No brand name provided'}), 400
        
    if not isinstance(days, (int, float)) or days <= 0:
        return jsonify({'error': 'Invalid days parameter. Must be a positive number.'}), 400
    
    try:
        result = analyzer.analyze_brand_mentions(brand, days)
        if 'error' in result:
            if 'API read limit reached' in result['error']:
                return jsonify(result), 429  # Too Many Requests
            elif 'Reddit API not properly initialized' in result['error']:
                return jsonify(result), 503  # Service Unavailable
            else:
                return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"[ERROR] /analyze-brand: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/usage-stats', methods=['GET'])
def get_usage_stats():
    if not analyzer:
        return jsonify({'error': 'Analyzer not initialized'}), 500
        
    try:
        stats = analyzer.get_usage_stats()
        return jsonify(stats)
    except Exception as e:
        import traceback
        print(f"[ERROR] /usage-stats: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 