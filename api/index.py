# import os
# from pathlib import Path
# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from vercel_python_wsgi import create_app as vercel_app

# # Adjust paths so static assets (index.html, chatbot.js, etc.) can be served
# BASE_DIR = Path(__file__).resolve().parent.parent
# STATIC_DIR = BASE_DIR

# # Import the core analyzer
# from sentiment_analyzer import SentimentAnalyzer  # noqa: E402

# app = Flask(__name__)
# CORS(app)

# analyzer = SentimentAnalyzer()

# @app.route('/')
# def serve_index():
#     return send_from_directory(STATIC_DIR, 'index.html')

# @app.route('/<path:path>')
# def serve_static(path):
#     return send_from_directory(STATIC_DIR, path)

# @app.route('/analyze', methods=['POST'])
# def analyze():
#     data = request.json or {}
#     text = data.get('text', '')
#     if not text:
#         return jsonify({'error': 'No text provided'}), 400
#     try:
#         result = analyzer.analyze_text(text)
#         if 'error' in result:
#             return jsonify(result), 400
#         return jsonify(result)
#     except Exception as exc:
#         return jsonify({'error': str(exc)}), 500

# @app.route('/analyze-brand', methods=['POST'])
# def analyze_brand():
#     data = request.json or {}
#     brand = data.get('brand', '')
#     days = data.get('days', 7)

#     if not brand:
#         return jsonify({'error': 'No brand name provided'}), 400
#     if not isinstance(days, (int, float)) or days <= 0:
#         return jsonify({'error': 'Invalid days parameter. Must be a positive number.'}), 400

#     try:
#         result = analyzer.analyze_brand_mentions(brand, days)
#         if 'error' in result:
#             return jsonify(result), 429 if 'limit' in result.get('error', '').lower() else 400
#         return jsonify(result)
#     except Exception as exc:
#         return jsonify({'error': str(exc)}), 500

# @app.route('/usage-stats', methods=['GET'])
# def get_usage_stats():
#     try:
#         stats = analyzer.get_usage_stats()
#         return jsonify(stats)
#     except Exception as exc:
#         return jsonify({'error': str(exc)}), 500

# # Vercel entrypoint
# handler = vercel_app(app)


import os
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from vercel_python_wsgi import make_handler  # <-- correct function

# Adjust paths so static assets (index.html, chatbot.js, etc.) can be served
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR

# Import the core analyzer
from sentiment_analyzer import SentimentAnalyzer  # noqa: E402

app = Flask(__name__)
CORS(app)

analyzer = SentimentAnalyzer()

@app.route('/')
def serve_index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_DIR, path)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    try:
        result = analyzer.analyze_text(text)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500

@app.route('/analyze-brand', methods=['POST'])
def analyze_brand():
    data = request.json or {}
    brand = data.get('brand', '')
    days = data.get('days', 7)

    if not brand:
        return jsonify({'error': 'No brand name provided'}), 400
    if not isinstance(days, (int, float)) or days <= 0:
        return jsonify({'error': 'Invalid days parameter. Must be a positive number.'}), 400

    try:
        result = analyzer.analyze_brand_mentions(brand, days)
        if 'error' in result:
            return jsonify(result), 429 if 'limit' in result.get('error', '').lower() else 400
        return jsonify(result)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500

@app.route('/usage-stats', methods=['GET'])
def get_usage_stats():
    try:
        stats = analyzer.get_usage_stats()
        return jsonify(stats)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500

# Vercel entrypoint (must be last)
handler = make_handler(app)  # <-- correct
