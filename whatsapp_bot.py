from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os
import re

app = Flask(__name__)

EVENTS_FILE = 'events.json'

# Categories mapping for natural language
CATEGORIES = {
    # 🏛 Politik & Geschichte
    'politik': '🏛 Politik & Geschichte',
    'geschichte': '🏛 Politik & Geschichte',
    'krieg': '🏛 Politik & Geschichte',
    'revolution': '🏛 Politik & Geschichte',
    'herrscher': '🏛 Politik & Geschichte',
    'vertrag': '🏛 Politik & Geschichte',
    'staatenbildung': '🏛 Politik & Geschichte',
    'political': '🏛 Politik & Geschichte',
    'history': '🏛 Politik & Geschichte',

    # 💰 Wirtschaft & Handel
    'wirtschaft': '💰 Wirtschaft & Handel',
    'handel': '💰 Wirtschaft & Handel',
    'ökonomie': '💰 Wirtschaft & Handel',
    'finanzen': '💰 Wirtschaft & Handel',
    'industrialisierung': '💰 Wirtschaft & Handel',
    'globalisierung': '💰 Wirtschaft & Handel',
    'handelswege': '💰 Wirtschaft & Handel',
    'wirtschaftskrise': '💰 Wirtschaft & Handel',
    'economy': '💰 Wirtschaft & Handel',
    'business': '💰 Wirtschaft & Handel',
    'trade': '💰 Wirtschaft & Handel',

    # 🧠 Wissenschaft & Entdeckungen
    'wissenschaft': '🧠 Wissenschaft & Entdeckungen',
    'entdeckung': '🧠 Wissenschaft & Entdeckungen',
    'medizin': '🧠 Wissenschaft & Entdeckungen',
    'astronomie': '🧠 Wissenschaft & Entdeckungen',
    'mathematik': '🧠 Wissenschaft & Entdeckungen',
    'naturwissenschaft': '🧠 Wissenschaft & Entdeckungen',
    'forschung': '🧠 Wissenschaft & Entdeckungen',
    'science': '🧠 Wissenschaft & Entdeckungen',
    'discovery': '🧠 Wissenschaft & Entdeckungen',

    # ⚙️ Technik & Erfindungen
    'technik': '⚙️ Technik & Erfindungen',
    'erfindung': '⚙️ Technik & Erfindungen',
    'technologie': '⚙️ Technik & Erfindungen',
    'maschine': '⚙️ Technik & Erfindungen',
    'computer': '⚙️ Technik & Erfindungen',
    'verkehrsmittel': '⚙️ Technik & Erfindungen',
    'werkzeug': '⚙️ Technik & Erfindungen',
    'technology': '⚙️ Technik & Erfindungen',
    'tech': '⚙️ Technik & Erfindungen',
    'invention': '⚙️ Technik & Erfindungen',

    # 🏗 Architektur & Bauwerke
    'architektur': '🏗 Architektur & Bauwerke',
    'bauwerk': '🏗 Architektur & Bauwerke',
    'bauwerke': '🏗 Architektur & Bauwerke',
    'gebäude': '🏗 Architektur & Bauwerke',
    'stadt': '🏗 Architektur & Bauwerke',
    'städte': '🏗 Architektur & Bauwerke',
    'bau': '🏗 Architektur & Bauwerke',
    'architecture': '🏗 Architektur & Bauwerke',
    'building': '🏗 Architektur & Bauwerke',

    # 🎨 Kunst & Kultur
    'kunst': '🎨 Kunst & Kultur',
    'kultur': '🎨 Kunst & Kultur',
    'malerei': '🎨 Kunst & Kultur',
    'musik': '🎨 Kunst & Kultur',
    'theater': '🎨 Kunst & Kultur',
    'film': '🎨 Kunst & Kultur',
    'mode': '🎨 Kunst & Kultur',
    'art': '🎨 Kunst & Kultur',
    'culture': '🎨 Kunst & Kultur',
    'music': '🎨 Kunst & Kultur',

    # 📚 Literatur & Philosophie
    'literatur': '📚 Literatur & Philosophie',
    'philosophie': '📚 Literatur & Philosophie',
    'autor': '📚 Literatur & Philosophie',
    'autoren': '📚 Literatur & Philosophie',
    'werk': '📚 Literatur & Philosophie',
    'werke': '📚 Literatur & Philosophie',
    'ideen': '📚 Literatur & Philosophie',
    'literature': '📚 Literatur & Philosophie',
    'philosophy': '📚 Literatur & Philosophie',

    # ✝️ Religion & Mythologie
    'religion': '✝️ Religion & Mythologie',
    'mythologie': '✝️ Religion & Mythologie',
    'mythos': '✝️ Religion & Mythologie',
    'reformation': '✝️ Religion & Mythologie',
    'religiös': '✝️ Religion & Mythologie',
    'glaube': '✝️ Religion & Mythologie',
    'mythology': '✝️ Religion & Mythologie',

    # ⚔️ Gesellschaft & Soziales
    'gesellschaft': '⚔️ Gesellschaft & Soziales',
    'soziales': '⚔️ Gesellschaft & Soziales',
    'frauenrechte': '⚔️ Gesellschaft & Soziales',
    'bildung': '⚔️ Gesellschaft & Soziales',
    'sklaverei': '⚔️ Gesellschaft & Soziales',
    'menschenrechte': '⚔️ Gesellschaft & Soziales',
    'migration': '⚔️ Gesellschaft & Soziales',
    'social': '⚔️ Gesellschaft & Soziales',
    'society': '⚔️ Gesellschaft & Soziales',

    # 🌍 Umwelt & Natur
    'umwelt': '🌍 Umwelt & Natur',
    'natur': '🌍 Umwelt & Natur',
    'naturkatastrophe': '🌍 Umwelt & Natur',
    'klima': '🌍 Umwelt & Natur',
    'klimawandel': '🌍 Umwelt & Natur',
    'ökologie': '🌍 Umwelt & Natur',
    'ressourcen': '🌍 Umwelt & Natur',
    'umweltschutz': '🌍 Umwelt & Natur',
    'environment': '🌍 Umwelt & Natur',
    'nature': '🌍 Umwelt & Natur',
    'climate': '🌍 Umwelt & Natur',
}

# Common regions with flags
REGIONS = {
    'mesopotamien': '🇮🇶 Mesopotamien',
    'irak': '🇮🇶 Irak',
    'griechenland': '🇬🇷 Griechenland',
    'deutschland': '🇩🇪 Deutschland',
    'frankreich': '🇫🇷 Frankreich',
    'england': '🇬🇧 England',
    'uk': '🇬🇧 England',
    'großbritannien': '🇬🇧 England',
    'usa': '🇺🇸 USA',
    'amerika': '🇺🇸 USA',
    'china': '🇨🇳 China',
    'japan': '🇯🇵 Japan',
    'indien': '🇮🇳 Indien',
    'russland': '🇷🇺 Russland',
    'italien': '🇮🇹 Italien',
    'spanien': '🇪🇸 Spanien',
    'weltweit': '🌍 Weltweit',
    'global': '🌍 Weltweit',
}

def load_events():
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_events(events):
    with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def parse_event_message(message):
    """
    Parse WhatsApp message into event format.
    Expected formats:
    - "1969 | Mondlandung | Technik | USA"
    - "1789, Französische Revolution, Politik, Frankreich"
    - "Jahr: 2020, Titel: COVID-19, Kategorie: Gesellschaft, Region: Weltweit"
    """
    message = message.strip()

    # Try pipe-separated format
    if '|' in message:
        parts = [p.strip() for p in message.split('|')]
        if len(parts) >= 4:
            year, title, category, region = parts[:4]
        elif len(parts) == 3:
            year, title, category = parts
            region = "Weltweit"
        else:
            return None

    # Try comma-separated format
    elif ',' in message:
        parts = [p.strip() for p in message.split(',')]
        if len(parts) >= 4:
            year, title, category, region = parts[:4]
        elif len(parts) == 3:
            year, title, category = parts
            region = "Weltweit"
        else:
            return None

    # Try key-value format
    elif ':' in message:
        event = {}
        for part in message.split(','):
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if 'jahr' in key or 'year' in key:
                    event['year'] = value
                elif 'titel' in key or 'title' in key:
                    event['title'] = value
                elif 'kategorie' in key or 'category' in key:
                    event['category'] = value
                elif 'region' in key:
                    event['region'] = value

        if all(k in event for k in ['year', 'title', 'category', 'region']):
            year = event['year']
            title = event['title']
            category = event['category']
            region = event['region']
        else:
            return None
    else:
        return None

    # Parse year (handle BC/v. Chr.)
    year = year.replace('Jahr:', '').strip()
    bc_markers = ['v. chr', 'v.chr', 'bc', 'v chr', 'vor christus']
    is_bc = any(marker in year.lower() for marker in bc_markers)

    # Extract numeric year
    year_match = re.search(r'(\d+)', year)
    if not year_match:
        return None

    year_num = int(year_match.group(1))
    if is_bc:
        year_num = -year_num

    # Normalize category
    category = category.replace('Kategorie:', '').strip()
    category_lower = category.lower()
    for key, value in CATEGORIES.items():
        if key in category_lower:
            category = value
            break

    # Normalize region
    region = region.replace('Region:', '').strip()
    region_lower = region.lower()
    for key, value in REGIONS.items():
        if key in region_lower:
            region = value
            break
    # If not in mapping, keep original but ensure it starts with emoji or add global emoji
    if not region.startswith('🇦') and not region.startswith('🌍'):
        region = f'🌍 {region}'

    return {
        'year': year_num,
        'title': title.strip(),
        'category': category,
        'region': region
    }

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')

    resp = MessagingResponse()
    msg = resp.message()

    if not incoming_msg:
        msg.body("Bitte sende ein Event im Format:\nJahr | Titel | Kategorie | Region\n\nBeispiel:\n1969 | Mondlandung | Technik | USA")
        return str(resp)

    # Check for help command
    if incoming_msg.lower() in ['hilfe', 'help', '?', 'kategorien']:
        help_text = """📅 Timeline Event Hinzufügen

Formate:
1. Jahr | Titel | Kategorie | Region
2. Jahr, Titel, Kategorie, Region

Kategorien:
🏛 Politik & Geschichte
💰 Wirtschaft & Handel
🧠 Wissenschaft & Entdeckungen
⚙️ Technik & Erfindungen
🏗 Architektur & Bauwerke
🎨 Kunst & Kultur
📚 Literatur & Philosophie
✝️ Religion & Mythologie
⚔️ Gesellschaft & Soziales
🌍 Umwelt & Natur

Beispiele:
✅ 1969 | Mondlandung | Wissenschaft | USA
✅ 1789, Französische Revolution, Politik, Frankreich
✅ 500 v. Chr. | Demokratie in Athen | Politik | Griechenland"""

        msg.body(help_text)
        return str(resp)

    # Parse the event
    event = parse_event_message(incoming_msg)

    if not event:
        msg.body("❌ Fehler beim Parsen. Nutze eines dieser Formate:\n\n1️⃣ Jahr | Titel | Kategorie | Region\n2️⃣ Jahr, Titel, Kategorie, Region\n\nBeispiel:\n1969 | Mondlandung | Technik | USA\n\nSchreibe 'Hilfe' für mehr Infos.")
        return str(resp)

    # Add event to timeline
    events = load_events()
    events.append(event)
    save_events(events)

    # Confirm
    confirmation = f"""✅ Event hinzugefügt!

📅 Jahr: {event['year']}
📝 Titel: {event['title']}
🏷️ Kategorie: {event['category']}
🌍 Region: {event['region']}

Dein Event wurde zur Timeline hinzugefügt!"""

    msg.body(confirmation)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
