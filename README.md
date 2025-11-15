# Historical Timeline with WhatsApp Integration

Add historical events to your interactive timeline via WhatsApp! Events are automatically formatted and validated.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
# Terminal 1: Start API
python api.py

# Terminal 2: Start WhatsApp bot
python whatsapp_bot.py

# Terminal 3: Serve frontend
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

### 3. Setup WhatsApp (Optional)
See `SETUP.md` for complete WhatsApp integration instructions using Twilio.

## Adding Events via WhatsApp

Send messages in this format:
```
Year | Title | Category | Region
```

**Examples:**
```
1969 | Mondlandung | Technik | USA
1789, Französische Revolution, Politik, Frankreich
500 v. Chr. | Demokratie in Athen | Politik, Griechenland
```

**Categories:**
- Politik & Geschichte
- Technik & Wissenschaft
- Wirtschaft
- Gesellschaft & Soziales

Send `hilfe` to the WhatsApp bot for more info.

## Hosting

**Easiest options:**
1. **Railway.app** - Auto-deploys from GitHub (recommended)
2. **Heroku** - Free tier available
3. **Netlify/Vercel** - For frontend only

See `SETUP.md` for detailed hosting instructions.

## Project Structure

```
timeline/
├── api.py              # Flask API server
├── whatsapp_bot.py     # WhatsApp webhook handler
├── index.html          # Timeline UI
├── script.js           # Frontend logic
├── style.css           # Styling
├── events.json         # Persistent event storage (auto-generated)
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── SETUP.md           # Detailed setup guide
```

## Features

- Interactive horizontal timeline
- Filter by category, region, or search
- Add events via WhatsApp or API
- Automatic year formatting (BC/AD)
- Flag emojis for regions
- Persistent JSON storage
- Natural language parsing

---

For complete setup and hosting instructions, see `SETUP.md`
