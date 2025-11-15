from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

EVENTS_FILE = 'events.json'

# Default events
DEFAULT_EVENTS = [
    {"year": -2000, "title": "Hochkulturen in Mesopotamien", "category": "Politik & Geschichte", "region": "🇮🇶 Mesopotamien"},
    {"year": -500,  "title": "Demokratie in Athen", "category": "Politik & Geschichte", "region": "🇬🇷 Griechenland"},
    {"year": 1440,  "title": "Buchdruck (Gutenberg)", "category": "Technik & Wissenschaft", "region": "🇩🇪 Deutschland"},
    {"year": 1789,  "title": "Französische Revolution", "category": "Politik & Geschichte", "region": "🇫🇷 Frankreich"},
    {"year": 1815,  "title": "Industrielle Revolution", "category": "Wirtschaft", "region": "🇬🇧 England"},
    {"year": 1969,  "title": "Mondlandung", "category": "Technik & Wissenschaft", "region": "🇺🇸 USA"},
    {"year": 2020,  "title": "COVID-19 Pandemie", "category": "Gesellschaft & Soziales", "region": "🌍 Weltweit"},
]

def load_events():
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_EVENTS.copy()

def save_events(events):
    with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

events = load_events()

@app.route('/events', methods=['GET'])
def get_events():
    return jsonify(events)

@app.route('/events', methods=['POST'])
def add_event():
    data = request.get_json()
    if not all(k in data for k in ("title", "year", "category", "region")):
        return jsonify({"error": "Missing field"}), 400
    events.append(data)
    save_events(events)
    return jsonify({"message": "Event added", "event": data}), 201

@app.route('/')
def home():
    return jsonify({"message": "Timeline API v1", "endpoints": ["/events (GET, POST)"]})

if __name__ == '__main__':
    app.run(debug=True, port=5001)

