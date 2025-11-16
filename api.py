from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import anthropic

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

def parse_event_with_llm(message):
    """Use Claude to intelligently parse event from natural language"""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        # Fallback to manual parsing
        from whatsapp_bot import parse_event_message
        return parse_event_message(message), None

    try:
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""Analysiere folgende Nachricht und extrahiere ein historisches Ereignis im JSON-Format:

Nachricht: "{message}"

Verfügbare Kategorien (mit Emoji):
- 🏛 Politik & Geschichte
- 💰 Wirtschaft & Handel
- 🧠 Wissenschaft & Entdeckungen
- ⚙️ Technik & Erfindungen
- 🏗 Architektur & Bauwerke
- 🎨 Kunst & Kultur
- 📚 Literatur & Philosophie
- ✝️ Religion & Mythologie
- ⚔️ Gesellschaft & Soziales
- 🌍 Umwelt & Natur
- 👤 Persönlichkeiten (für historische Personen - nutze Geburtsjahr als "year")

Aufgabe:
1. Extrahiere: Jahr (bei Personen: Geburtsjahr), Titel, wähle passende Kategorie, Region
2. Füge Flaggen-Emoji zur Region hinzu (🇩🇪 Deutschland, 🇫🇷 Frankreich, etc.)
3. Erstelle 3-5 kurze, prägnante Bullet Points OHNE Metadata (kein Jahr, keine Region nennen)

Beispiel für Person:
{{
  "year": 1769,
  "title": "Alexander von Humboldt",
  "category": "👤 Persönlichkeiten",
  "region": "🇩🇪 Deutschland",
  "summary": [
    "Naturforscher und bedeutendster Wissenschaftler seiner Zeit",
    "Erforschte Südamerika und dokumentierte Flora, Fauna und Geologie",
    "Begründer der modernen Geographie und Ökologie",
    "Sein Werk beeinflusste Darwin und die Evolutionstheorie"
  ]
}}

Beispiel für Ereignis:
{{
  "year": 1945,
  "title": "Ende 2. Weltkrieg",
  "category": "🏛 Politik & Geschichte",
  "region": "🌍 Weltweit",
  "summary": [
    "Begann durch Überfall Deutschlands auf Polen",
    "Endete mit Kapitulation Deutschlands und Japans",
    "Über 60 Millionen Tote weltweit",
    "Führte zur Gründung der Vereinten Nationen"
  ]
}}

Antworte NUR mit dem JSON (keine Erklärung):"""

        message_response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse JSON from response
        response_text = message_response.content[0].text.strip()

        # Extract JSON from response (in case there's extra text)
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            event_data = json.loads(json_match.group())
            summary = event_data.pop('summary', None)
            return event_data, summary
        else:
            return None, None

    except Exception as e:
        print(f"LLM parsing error: {e}")
        # Fallback
        from whatsapp_bot import parse_event_message
        return parse_event_message(message), None

@app.route('/events/telegram', methods=['POST'])
def add_event_telegram():
    """
    Smart endpoint for n8n/Telegram integration with LLM parsing.

    Accepts natural language or structured format:
    - "1945 Ende 2. Weltkrieg Deutschland"
    - "1969 | Mondlandung | Wissenschaft | USA"
    - "Im Jahr 1789 begann die Französische Revolution"
    """
    data = request.get_json()

    # Handle both direct text and n8n message format
    message = data.get('message') or data.get('text') or data.get('Body', '')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Try LLM-powered parsing first
    event, summary = parse_event_with_llm(message)

    if not event:
        return jsonify({
            "error": "Could not parse message",
            "message": message,
            "hint": "Try format: 'Jahr Titel Region' or 'Year | Title | Category | Region'"
        }), 400

    # Add to events
    events.append(event)
    save_events(events)

    # Also cache the summary if generated
    if summary:
        cache_key = f"{event['title']}_{event['year']}"
        # We'll need to store this somewhere accessible to the frontend
        # For now, we could add it to the event itself
        event['_summary'] = summary

    return jsonify({
        "success": True,
        "message": "Event added successfully",
        "event": event,
        "summary": summary
    }), 201

@app.route('/events/summary', methods=['POST'])
def generate_summary():
    """
    Generate AI summary for an event using Claude API
    """
    event = request.get_json()

    if not event or 'title' not in event:
        return jsonify({"error": "Invalid event data"}), 400

    # Check for API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("WARNING: No ANTHROPIC_API_KEY found, using fallback summary")
        # Return fallback summary if no API key
        return jsonify({
            "summary": generate_fallback_summary(event),
            "fallback": True
        })

    print(f"Generating summary for: {event.get('title', 'Unknown')}")

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Build context-aware prompt
        event_context = f"Ereignis: {event['title']}"
        if event.get('year'):
            year_str = f"{abs(event['year'])} {'v. Chr.' if event['year'] < 0 else 'n. Chr.'}"
            event_context += f" ({year_str})"
        if event.get('region'):
            event_context += f", Region: {event['region']}"

        prompt = f"""Erstelle eine prägnante Zusammenfassung für dieses historische Ereignis:

{event_context}

Anforderungen:
- Genau 3-5 kurze Bullet Points
- Jeder Punkt max. 1 Satz, sehr präzise und spezifisch für DIESES Ereignis
- KEINE Metadata (kein Jahr, keine Region nennen - das steht schon oben)
- Fokus: Ursachen, wichtige Fakten, Verlauf, Auswirkungen, Bedeutung
- Sei SPEZIFISCH - nicht generisch!

Beispiel für "Französische Revolution (1789)":
Begann durch wirtschaftliche Krise und Unzufriedenheit mit dem Königshaus
Sturm auf die Bastille am 14. Juli 1789 als Wendepunkt
König Ludwig XVI wurde 1793 hingerichtet
Führte zur Erklärung der Menschenrechte
Endete mit Napoleons Machtübernahme

Antworte NUR mit den Bullet Points (OHNE Bindestriche oder Nummerierung):"""

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Cheaper model
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        summary_text = message.content[0].text
        bullet_points = [line.strip().lstrip('-•').strip()
                        for line in summary_text.split('\n')
                        if line.strip() and not line.strip().startswith('#')]

        # Ensure we have exactly 5 points
        bullet_points = bullet_points[:5]
        while len(bullet_points) < 5:
            bullet_points.append("Weitere Informationen werden noch recherchiert")

        return jsonify({"summary": bullet_points})

    except Exception as e:
        print(f"Error generating summary: {e}")
        return jsonify({
            "summary": generate_fallback_summary(event)
        })

def generate_fallback_summary(event):
    """Generate a simple fallback summary without AI"""
    title = event.get('title', 'Ereignis')
    return [
        f"Keine automatische Zusammenfassung für '{title}' verfügbar",
        "Bitte ANTHROPIC_API_KEY in Railway Environment Variables setzen",
        "Dann werden AI-generierte Zusammenfassungen angezeigt"
    ]

@app.route('/api')
def api_info():
    return jsonify({
        "message": "Timeline API v1",
        "endpoints": [
            "/events (GET, POST)",
            "/events/telegram (POST) - for n8n/Telegram integration",
            "/events/summary (POST) - Generate AI summary for event"
        ]
    })

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory('.', 'script.js')

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)

