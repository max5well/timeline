# n8n + Telegram Integration

So kannst du Events über Telegram zu deiner Timeline hinzufügen.

## Schritt 1: API hosten

### Option A: Railway (Empfohlen - 5 Minuten)

1. Gehe zu https://railway.app
2. Sign in with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Wähle `max5well/timeline`
5. Railway erkennt automatisch Python/Flask
6. Nach dem Deploy bekommst du eine URL wie: `https://timeline-production-xxxx.up.railway.app`

**Wichtig:** Notiere dir diese URL!

### Option B: Render.com (Auch kostenlos)

1. Gehe zu https://render.com
2. "New" → "Web Service"
3. Connect GitHub repo: `max5well/timeline`
4. Settings:
   - Name: `timeline-api`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn api:app`
5. Deploy!

---

## Schritt 2: n8n Workflow erstellen

### n8n Setup

Falls du n8n noch nicht hast:
- **Cloud:** https://n8n.io (einfachste Option)
- **Self-hosted:** `npx n8n` oder Docker

### Workflow Schritte

1. **Neuen Workflow erstellen**

2. **Node 1: Telegram Trigger**
   - Node hinzufügen: "Telegram Trigger"
   - Bot Token erstellen:
     - Öffne Telegram
     - Suche nach `@BotFather`
     - Sende `/newbot`
     - Folge den Anweisungen
     - Kopiere den Bot Token
   - Füge Token in n8n ein
   - Aktiviere den Trigger

3. **Node 2: HTTP Request**
   - Node hinzufügen: "HTTP Request"
   - Method: `POST`
   - URL: `https://DEINE-RAILWAY-URL.up.railway.app/events/telegram`
   - Authentication: None
   - Body Content Type: `JSON`
   - Body:
     ```json
     {
       "message": "{{ $json.message.text }}"
     }
     ```

4. **Node 3: Telegram Response (Optional)**
   - Node hinzufügen: "Telegram"
   - Operation: "Send Message"
   - Chat ID: `{{ $json.message.chat.id }}`
   - Text:
     ```
     ✅ Event hinzugefügt!
     {{ $node["HTTP Request"].json.event.title }}
     ```

5. **Workflow aktivieren** (Toggle oben rechts)

---

## Schritt 3: Events hinzufügen

Öffne deinen Telegram Bot und sende Nachrichten wie:

```
1945 | Ende 2. Weltkrieg | Politik | Deutschland
```

```
1969 | Mondlandung | Wissenschaft | USA
```

```
500 v. Chr. | Demokratie in Athen | Politik | Griechenland
```

### Format

```
Jahr | Titel | Kategorie | Region
```

**Kategorien** (Keywords werden automatisch erkannt):
- 🏛 Politik & Geschichte → `politik`, `geschichte`, `krieg`, `revolution`
- 💰 Wirtschaft & Handel → `wirtschaft`, `handel`, `industrie`
- 🧠 Wissenschaft & Entdeckungen → `wissenschaft`, `entdeckung`, `medizin`
- ⚙️ Technik & Erfindungen → `technik`, `erfindung`, `computer`
- 🏗 Architektur & Bauwerke → `architektur`, `bauwerk`, `stadt`
- 🎨 Kunst & Kultur → `kunst`, `kultur`, `musik`, `film`
- 📚 Literatur & Philosophie → `literatur`, `philosophie`, `autor`
- ✝️ Religion & Mythologie → `religion`, `mythologie`, `glaube`
- ⚔️ Gesellschaft & Soziales → `gesellschaft`, `soziales`, `bildung`
- 🌍 Umwelt & Natur → `umwelt`, `natur`, `klima`

**Regionen** werden automatisch mit Flaggen versehen:
- Deutschland → 🇩🇪 Deutschland
- USA → 🇺🇸 USA
- Frankreich → 🇫🇷 Frankreich
- etc.

---

## n8n Workflow als JSON

Hier ist der fertige Workflow zum Importieren:

```json
{
  "name": "Timeline Telegram Bot",
  "nodes": [
    {
      "parameters": {},
      "name": "Telegram Trigger",
      "type": "n8n-nodes-base.telegramTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "https://DEINE-URL.up.railway.app/events/telegram",
        "options": {},
        "bodyParametersJson": "={{ JSON.stringify({ message: $json.message.text }) }}"
      },
      "name": "HTTP Request",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [450, 300]
    },
    {
      "parameters": {
        "chatId": "={{ $json.message.chat.id }}",
        "text": "=✅ Event hinzugefügt!\n{{ $node['HTTP Request'].json.event.title }}"
      },
      "name": "Telegram Response",
      "type": "n8n-nodes-base.telegram",
      "typeVersion": 1,
      "position": [650, 300]
    }
  ],
  "connections": {
    "Telegram Trigger": {
      "main": [[{ "node": "HTTP Request", "type": "main", "index": 0 }]]
    },
    "HTTP Request": {
      "main": [[{ "node": "Telegram Response", "type": "main", "index": 0 }]]
    }
  }
}
```

**Wichtig:** Ersetze `DEINE-URL` mit deiner Railway URL!

---

## Testen

1. Sende eine Nachricht an deinen Telegram Bot:
   ```
   2024 | n8n Integration | Technik | Weltweit
   ```

2. Du solltest eine Bestätigung bekommen:
   ```
   ✅ Event hinzugefügt!
   n8n Integration
   ```

3. Öffne deine Timeline: Das Event sollte erscheinen!

---

## Troubleshooting

### Bot antwortet nicht
- Prüfe ob n8n Workflow aktiviert ist
- Prüfe Telegram Bot Token
- Schaue in n8n Execution Log

### Event wird nicht hinzugefügt
- Prüfe Railway/Render Logs
- Teste API direkt:
  ```bash
  curl -X POST https://DEINE-URL.up.railway.app/events/telegram \
    -H "Content-Type: application/json" \
    -d '{"message": "2024 | Test | Technik | Deutschland"}'
  ```

### Format Fehler
- Nutze immer: `Jahr | Titel | Kategorie | Region`
- Verwende `|` als Trennzeichen
- Mindestens 3 Felder (Region ist optional)

---

## Bonus: Erweiterte Features

### 1. Spracherkennung
Füge einen "Whisper" Node hinzu für Sprach-zu-Text

### 2. KI-Parser
Nutze OpenAI Node um natürliche Sprache zu parsen:
```
"Füge hinzu: Im Jahr 1945 endete der 2. Weltkrieg"
→ Wird zu: "1945 | Ende 2. Weltkrieg | Politik | Deutschland"
```

### 3. Bilder Support
Erweitere die API um Bild-URLs zu speichern

---

Viel Erfolg! 🚀
