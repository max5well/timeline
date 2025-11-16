from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='.')
CORS(app)

EVENTS_FILE = 'events.json'

# Default events
DEFAULT_EVENTS = [
    {"year": -2000, "title": "Hochkulturen in Mesopotamien", "category": "🏛 Politik & Geschichte", "region": "🇮🇶 Mesopotamien"},
    {"year": -500,  "title": "Demokratie in Athen", "category": "🏛 Politik & Geschichte", "region": "🇬🇷 Griechenland"},
    {"year": 1440,  "title": "Buchdruck (Gutenberg)", "category": "⚙️ Technik & Erfindungen", "region": "🇩🇪 Deutschland"},
    {"year": 1789,  "title": "Französische Revolution", "category": "🏛 Politik & Geschichte", "region": "🇫🇷 Frankreich"},
    {"year": 1815,  "title": "Industrielle Revolution", "category": "💰 Wirtschaft & Handel", "region": "🇬🇧 England"},
    {"year": 1969,  "title": "Mondlandung", "category": "🧠 Wissenschaft & Entdeckungen", "region": "🇺🇸 USA"},
    {"year": 2020,  "title": "COVID-19 Pandemie", "category": "⚔️ Gesellschaft & Soziales", "region": "🌍 Weltweit"},
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

@app.route('/events/telegram', methods=['POST'])
def add_event_telegram():
    """
    Simplified endpoint for n8n/Telegram integration.
    Accepts simple text format and parses it.

    Expected format: "Year | Title | Category | Region"
    Example: "1945 | Ende 2. Weltkrieg | Politik | Deutschland"
    """
    data = request.get_json()

    # Handle both direct text and n8n message format
    message = data.get('message') or data.get('text') or data.get('Body', '')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Parse the message
    from whatsapp_bot import parse_event_message
    event = parse_event_message(message)

    if not event:
        return jsonify({
            "error": "Could not parse message",
            "message": message,
            "format": "Expected: Year | Title | Category | Region",
            "example": "1945 | Ende 2. Weltkrieg | Politik | Deutschland"
        }), 400

    # Add to events
    events.append(event)
    save_events(events)

    return jsonify({
        "success": True,
        "message": "Event added successfully",
        "event": event
    }), 201

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api')
def api_info():
    return jsonify({
        "message": "Timeline API v1",
        "endpoints": [
            "/events (GET, POST)",
            "/events/telegram (POST) - for n8n/Telegram integration"
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)

