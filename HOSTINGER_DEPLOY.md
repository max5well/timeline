# Timeline auf Hostinger hosten

## Voraussetzungen

- Hostinger Account mit Python Support (VPS oder Cloud Hosting)
- SSH Zugang
- Domain (optional)

---

## Option 1: VPS/Cloud Hosting (Empfohlen)

### Schritt 1: SSH Verbindung

```bash
ssh root@your-server-ip
```

### Schritt 2: Python & Dependencies installieren

```bash
# System updaten
apt update && apt upgrade -y

# Python und pip installieren
apt install python3 python3-pip python3-venv nginx -y

# Git installieren (falls nicht vorhanden)
apt install git -y
```

### Schritt 3: Repository klonen

```bash
# Verzeichnis erstellen
mkdir -p /var/www
cd /var/www

# Repository klonen
git clone https://github.com/max5well/timeline.git
cd timeline

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### Schritt 4: Systemd Service erstellen

**API Service:**

```bash
nano /etc/systemd/system/timeline-api.service
```

Füge ein:

```ini
[Unit]
Description=Timeline API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/timeline
Environment="PATH=/var/www/timeline/venv/bin"
ExecStart=/var/www/timeline/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 api:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Speichern: `Ctrl+X`, dann `Y`, dann `Enter`

**Service starten:**

```bash
systemctl daemon-reload
systemctl start timeline-api
systemctl enable timeline-api
systemctl status timeline-api
```

### Schritt 5: Nginx konfigurieren

```bash
nano /etc/nginx/sites-available/timeline
```

Füge ein:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # oder deine Server-IP

    # Frontend (HTML, CSS, JS)
    location / {
        root /var/www/timeline;
        index index.html;
        try_files $uri $uri/ =404;
    }

    # API Endpunkt
    location /api/ {
        proxy_pass http://127.0.0.1:5001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Aktivieren:**

```bash
ln -s /etc/nginx/sites-available/timeline /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Schritt 6: Frontend anpassen

```bash
nano /var/www/timeline/script.js
```

Ändere Zeile 8:

```javascript
const res = await fetch('http://127.0.0.1:5001/events');
```

Zu:

```javascript
const res = await fetch('/api/events');
```

### Schritt 7: SSL Zertifikat (Optional aber empfohlen)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## Option 2: Shared Hosting mit Python Support

Falls Hostinger Shared Hosting mit Python App Support:

### Über Hostinger Control Panel

1. **Login** zu hPanel
2. **Website** → **Python App**
3. **Create Application**:
   - Python Version: 3.8+
   - Application Root: `/public_html/timeline`
   - Application URL: `your-domain.com`
   - Application Startup File: `api.py`

4. **SSH aktivieren** (in hPanel)

5. **Via SSH verbinden und Setup**:

```bash
ssh u123456789@your-domain.com

cd ~/public_html/timeline
git clone https://github.com/max5well/timeline.git .
pip install -r requirements.txt
```

6. **Passenger konfigurieren** (`passenger_wsgi.py`):

```python
import sys
import os

INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'timeline', '3.9', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, os.path.dirname(__file__))

from api import app as application
```

---

## n8n Integration für Hostinger

### Endpunkt URL

Nach dem Deployment ist dein API Endpunkt:

```
https://your-domain.com/api/events/telegram
```

### n8n HTTP Request Node

```json
{
  "url": "https://your-domain.com/api/events/telegram",
  "method": "POST",
  "body": {
    "message": "{{ $json.message.text }}"
  }
}
```

---

## Updates deployen

```bash
cd /var/www/timeline
git pull origin main
systemctl restart timeline-api
```

---

## Monitoring & Logs

### API Logs anschauen

```bash
journalctl -u timeline-api -f
```

### Nginx Logs

```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Service Status prüfen

```bash
systemctl status timeline-api
systemctl status nginx
```

---

## Firewall Setup

```bash
# UFW Firewall aktivieren
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

---

## Sicherheit

### 1. API Key Protection (Optional)

Füge in `api.py` hinzu:

```python
API_KEY = os.environ.get('API_KEY', 'your-secret-key')

@app.route('/events/telegram', methods=['POST'])
def add_event_telegram():
    auth_header = request.headers.get('Authorization')
    if auth_header != f'Bearer {API_KEY}':
        return jsonify({"error": "Unauthorized"}), 401
    # ... rest of code
```

In n8n füge Header hinzu:
```json
{
  "Authorization": "Bearer your-secret-key"
}
```

### 2. Rate Limiting

```bash
pip install flask-limiter
```

In `api.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/events/telegram', methods=['POST'])
@limiter.limit("10 per minute")
def add_event_telegram():
    # ...
```

---

## Kosten

**Hostinger VPS:**
- ab ~4€/Monat
- Volle Kontrolle
- Unbegrenzte Apps

**Hostinger Shared:**
- ab ~2€/Monat
- Eingeschränkter Python Support
- Einfacher Setup

---

## Troubleshooting

### "502 Bad Gateway"
- Prüfe ob timeline-api läuft: `systemctl status timeline-api`
- Prüfe Logs: `journalctl -u timeline-api -n 50`

### "Connection refused"
- Prüfe Port 5001: `netstat -tlnp | grep 5001`
- Prüfe Firewall: `ufw status`

### Events werden nicht gespeichert
- Prüfe Schreibrechte: `chown -R www-data:www-data /var/www/timeline`
- Prüfe ob events.json existiert: `ls -la /var/www/timeline/events.json`

---

## Backup Setup

```bash
# Cron Job für tägliches Backup
crontab -e
```

Füge hinzu:

```bash
0 2 * * * cp /var/www/timeline/events.json /var/backups/timeline-$(date +\%Y\%m\%d).json
```

---

Fertig! Deine Timeline läuft jetzt auf Hostinger 🚀

**Nächste Schritte:**
1. Öffne `https://your-domain.com`
2. Richte n8n ein mit `https://your-domain.com/api/events/telegram`
3. Sende Events via Telegram!
