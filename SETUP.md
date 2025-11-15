# Timeline Setup & Hosting Guide

## Features
- Interactive historical timeline visualization
- Add events via WhatsApp in natural language
- Automatic event formatting and validation
- Persistent JSON storage

---

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 2. WhatsApp Integration Setup

### Step 1: Create Twilio Account
1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free account
3. Verify your phone number

### Step 2: Enable WhatsApp Sandbox
1. In Twilio Console, go to **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Follow instructions to connect your WhatsApp to the sandbox
3. Send the join code (e.g., `join <your-code>`) to the Twilio WhatsApp number

### Step 3: Configure Webhook
You need a public URL for Twilio to send messages to. Use one of these options:

**Option A: ngrok (for testing)**
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/download

# Start your WhatsApp bot
python whatsapp_bot.py

# In another terminal, start ngrok
ngrok http 5002

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Option B: Deploy to a server (see Hosting section below)**

### Step 4: Set Webhook URL in Twilio
1. In Twilio Console, go to **Messaging** → **Settings** → **WhatsApp sandbox settings**
2. Set **When a message comes in** to: `https://your-url/whatsapp`
3. Save

---

## 3. Running Locally

### Start the Timeline API
```bash
python api.py
```
The API runs on http://localhost:5001

### Start the WhatsApp Bot
```bash
python whatsapp_bot.py
```
The bot runs on http://localhost:5002

### Open the Timeline
Open `index.html` in your browser, or serve it:
```bash
python -m http.server 8000
```
Then visit http://localhost:8000

---

## 4. Adding Events via WhatsApp

### Supported Formats

**Format 1: Pipe-separated**
```
1969 | Mondlandung | Technik | USA
```

**Format 2: Comma-separated**
```
1789, Französische Revolution, Politik, Frankreich
```

**Format 3: BC/v. Chr. dates**
```
500 v. Chr. | Demokratie in Athen | Politik | Griechenland
```

### Categories
- Politik & Geschichte
- Technik & Wissenschaft
- Wirtschaft
- Gesellschaft & Soziales

### Regions
Common regions are auto-formatted with flags:
- Deutschland → 🇩🇪 Deutschland
- USA → 🇺🇸 USA
- Frankreich → 🇫🇷 Frankreich
- Weltweit → 🌍 Weltweit

### Get Help
Send `hilfe` or `help` to the WhatsApp bot for formatting instructions.

---

## 5. Hosting Your Timeline

### Option 1: Heroku (Free Tier Available)

**Deploy API & WhatsApp Bot:**

1. Install Heroku CLI:
```bash
brew tap heroku/brew && brew install heroku  # macOS
```

2. Create `Procfile`:
```bash
echo "web: gunicorn api:app --bind 0.0.0.0:\$PORT" > Procfile
echo "whatsapp: gunicorn whatsapp_bot:app --bind 0.0.0.0:\$PORT" > Procfile.whatsapp
```

3. Initialize git and deploy:
```bash
git init
git add .
git commit -m "Initial commit"

heroku create your-timeline-api
git push heroku main

# For WhatsApp bot, create another Heroku app
heroku create your-timeline-whatsapp
# You'll need to configure this separately
```

4. Update Twilio webhook to your Heroku URL: `https://your-timeline-whatsapp.herokuapp.com/whatsapp`

**Deploy Frontend:**
- Upload `index.html`, `script.js`, `style.css` to any static hosting:
  - GitHub Pages (free)
  - Netlify (free)
  - Vercel (free)

5. Update `script.js` line 8 to point to your Heroku API:
```javascript
const res = await fetch('https://your-timeline-api.herokuapp.com/events');
```

---

### Option 2: Railway.app (Recommended - Simple & Free)

1. Go to https://railway.app
2. Sign up with GitHub
3. Create new project → Deploy from GitHub
4. Connect your repository
5. Railway auto-detects Flask and deploys
6. Get your public URL from Railway dashboard
7. Update Twilio webhook with Railway URL

---

### Option 3: DigitalOcean / AWS / Google Cloud

**For VPS deployment:**

1. Create a server (Ubuntu 22.04 recommended)

2. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip nginx
pip3 install -r requirements.txt
```

3. Set up systemd services:

**API Service** (`/etc/systemd/system/timeline-api.service`):
```ini
[Unit]
Description=Timeline API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/timeline
ExecStart=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:5001 api:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**WhatsApp Bot Service** (`/etc/systemd/system/timeline-whatsapp.service`):
```ini
[Unit]
Description=Timeline WhatsApp Bot
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/timeline
ExecStart=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:5002 whatsapp_bot:app
Restart=always

[Install]
WantedBy=multi-user.target
```

4. Configure nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /var/www/timeline;
        index index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5001/;
    }

    location /whatsapp {
        proxy_pass http://127.0.0.1:5002/whatsapp;
    }
}
```

5. Start services:
```bash
sudo systemctl start timeline-api
sudo systemctl start timeline-whatsapp
sudo systemctl enable timeline-api
sudo systemctl enable timeline-whatsapp
sudo systemctl restart nginx
```

6. Get SSL certificate (recommended):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 6. Testing

### Test the API directly:
```bash
curl -X POST http://localhost:5001/events \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2024,
    "title": "Test Event",
    "category": "Technik & Wissenschaft",
    "region": "🇩🇪 Deutschland"
  }'
```

### Test WhatsApp bot locally:
```bash
curl -X POST http://localhost:5002/whatsapp \
  -d "Body=1969 | Mondlandung | Technik | USA"
```

---

## Troubleshooting

### Events not saving
- Check that `events.json` has write permissions
- Verify API is running on port 5001

### WhatsApp not responding
- Ensure webhook URL is publicly accessible (use ngrok for testing)
- Check Twilio webhook logs in console
- Verify WhatsApp bot is running on correct port

### Timeline not loading
- Check browser console for CORS errors
- Ensure API URL in `script.js` is correct
- Verify Flask CORS is enabled

---

## Next Steps

- Add authentication for the API
- Implement event editing/deletion
- Add image support for events
- Create mobile-responsive design
- Add export functionality (PDF, CSV)

---

Enjoy your interactive timeline! 🎉
