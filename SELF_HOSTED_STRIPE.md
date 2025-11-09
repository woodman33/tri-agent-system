# Self-Hosted Stripe Integration
## 100% Open Source, No Third-Party Data Retention

### Architecture

```
Users → GitHub (clone code for free)
     ↓
Users → Stripe Checkout (hosted by Stripe, necessary for payments)
     ↓
Stripe → YOUR Mac/VPS Webhook (you control the server)
     ↓
License stored LOCALLY (JSON file or SQLite on YOUR machine)
```

**Data flows:**
- Stripe only sees: email, payment info (required for payment processing)
- Your server receives: webhook notification
- License stored: On YOUR machine only
- No Railway, no Heroku, no third-party storage

---

## Option 1: Run on Your Mac (Development/Testing)

### Setup Ngrok for Local Webhook Testing

Ngrok creates a temporary public URL that tunnels to your localhost.

```bash
# Install ngrok
brew install ngrok

# Start your FastAPI server locally
cd ~/multiagent-frameworks/tri-agent-system/monetization/backend
uvicorn stripe_integration:app --host 127.0.0.1 --port 8002

# In another terminal, start ngrok
ngrok http 8002

# Ngrok gives you a URL like: https://abc123.ngrok.io
# This tunnels to your localhost:8002
```

**Configure Stripe webhook:**
- URL: `https://abc123.ngrok.io/webhooks/stripe`
- This forwards to your Mac

**Pros:**
- Zero cost
- Full control
- No data leaves your machine (except to Stripe for payment)

**Cons:**
- Your Mac must be running 24/7 for webhooks
- Ngrok free tier resets URL on restart

---

## Option 2: Self-Hosted VPS (Production)

Use a cheap VPS you control completely. No managed platforms.

### Recommended: Hetzner Cloud (Germany, privacy-focused)

**Cost:** €4.15/month (~$4.50/month)
**Specs:** 2 vCPU, 2GB RAM, 40GB SSD
**Why:** EU-based, no surveillance, open-source friendly

```bash
# 1. Create Hetzner account at hetzner.com
# 2. Create a server (Ubuntu 22.04)
# 3. SSH into your server

ssh root@your-server-ip

# 4. Install dependencies
apt update
apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx

# 5. Create app directory
mkdir -p /opt/doubledown-studios
cd /opt/doubledown-studios

# 6. Upload your code
# From your Mac:
scp -r ~/multiagent-frameworks/tri-agent-system/monetization/backend root@your-server-ip:/opt/doubledown-studios/

# 7. Set up Python environment
cd /opt/doubledown-studios/backend
python3 -m venv venv
source venv/bin/activate
pip install stripe fastapi uvicorn

# 8. Create systemd service for auto-restart
cat > /etc/systemd/system/doubledown-api.service << 'EOF'
[Unit]
Description=Double Down Studios API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/doubledown-studios/backend
Environment="STRIPE_SECRET_KEY=sk_live_YOUR_KEY"
Environment="STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET"
ExecStart=/opt/doubledown-studios/backend/venv/bin/uvicorn stripe_integration:app --host 0.0.0.0 --port 8002
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 9. Start service
systemctl daemon-reload
systemctl enable doubledown-api
systemctl start doubledown-api

# 10. Set up Nginx reverse proxy
cat > /etc/nginx/sites-available/doubledown-api << 'EOF'
server {
    listen 80;
    server_name api.doubledownstudios.com;  # Your domain

    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/doubledown-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# 11. Get free SSL certificate (Let's Encrypt)
certbot --nginx -d api.doubledownstudios.com
```

**Configure Stripe webhook:**
- URL: `https://api.doubledownstudios.com/webhooks/stripe`

**Your domain setup:**
1. Buy domain at Namecheap/Porkbun (~$10/year)
2. Point A record to your VPS IP
3. Let's Encrypt handles SSL (free)

---

## Option 3: Run at Home with Dynamic DNS (Free VPS Alternative)

If you have a home internet connection with open ports:

```bash
# Use your Mac or a Raspberry Pi at home

# 1. Get free dynamic DNS from NoIP.com or DuckDNS.org
# Example: doubledown.duckdns.org

# 2. Forward port 8002 in your router to your Mac

# 3. Run FastAPI with systemd (on Mac, use launchd instead)
cd ~/multiagent-frameworks/tri-agent-system/monetization/backend
uvicorn stripe_integration:app --host 0.0.0.0 --port 8002

# 4. Set up SSL with Caddy (automatic HTTPS)
brew install caddy

# Caddyfile:
cat > Caddyfile << 'EOF'
doubledown.duckdns.org {
    reverse_proxy localhost:8002
}
EOF

sudo caddy run
```

**Configure Stripe webhook:**
- URL: `https://doubledown.duckdns.org/webhooks/stripe`

**Pros:**
- Zero cost
- Runs on your hardware at home
- Full control

**Cons:**
- Home IP might change (dynamic DNS handles this)
- ISP might block port 443 (use Cloudflare tunnel as alternative)

---

## Option 4: Cloudflare Tunnel (No Port Forwarding Needed)

If your ISP blocks ports or you don't want to expose your home IP:

```bash
# 1. Install Cloudflare Tunnel
brew install cloudflare/cloudflare/cloudflared

# 2. Login to Cloudflare
cloudflared tunnel login

# 3. Create tunnel
cloudflared tunnel create doubledown-api

# 4. Configure tunnel
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: YOUR_TUNNEL_ID
credentials-file: /Users/willmeldman/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: api.doubledownstudios.com
    service: http://localhost:8002
  - service: http_status:404
EOF

# 5. Route DNS
cloudflared tunnel route dns doubledown-api api.doubledownstudios.com

# 6. Run tunnel
cloudflared tunnel run doubledown-api
```

**What Cloudflare sees:**
- Encrypted traffic only
- No license data (just proxying)
- Free tier available

**Your FastAPI runs locally**, Cloudflare just tunnels requests.

---

## License Storage (100% Local)

Your webhook server stores licenses **only on your machine**:

### Current Implementation (JSON File)

```python
# In stripe_integration.py
def _save_license(self, **kwargs):
    license_db = Path.home() / '.doubledown-studios' / 'licenses.json'
    # Stored at: ~/.doubledown-studios/licenses.json
    # Only on YOUR machine
```

### Alternative: SQLite (Still Local)

```python
import sqlite3

def _save_license(self, **kwargs):
    db_path = Path.home() / '.doubledown-studios' / 'licenses.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            license_key TEXT PRIMARY KEY,
            email TEXT,
            tier TEXT,
            created_at TEXT,
            valid INTEGER
        )
    ''')

    cursor.execute('''
        INSERT INTO licenses VALUES (?, ?, ?, ?, ?)
    ''', (kwargs['license_key'], kwargs['email'], kwargs['tier'],
          datetime.now().isoformat(), 1))

    conn.commit()
    conn.close()
```

**Data location:** `~/.doubledown-studios/licenses.db` (your machine only)

---

## Environment Variables (Secure Storage)

Never hardcode Stripe keys. Use environment variables:

```bash
# Create .env file (NEVER commit to git)
cat > ~/multiagent-frameworks/tri-agent-system/monetization/backend/.env << 'EOF'
STRIPE_SECRET_KEY=sk_live_YOUR_ACTUAL_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_ACTUAL_SECRET
EOF

# Add to .gitignore
echo ".env" >> ~/multiagent-frameworks/tri-agent-system/.gitignore
```

Load in Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads from .env file

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
```

---

## Complete Self-Hosted Flow

1. **User clones from GitHub** (free, public repo)
2. **User clicks "Upgrade to Enterprise"** in app
3. **Opens Stripe checkout** (Stripe.com - necessary for payment processing)
4. **Payment succeeds** → Stripe webhook fires to YOUR server
5. **Your Mac/VPS receives webhook** → Generates license
6. **License saved to YOUR machine** (`~/.doubledown-studios/licenses.json`)
7. **Email sent to user** (via Stripe's email or your SMTP)
8. **User enters license in app** → Validates against YOUR server
9. **Features unlock**

**Data retention:**
- GitHub: Code only (public)
- Stripe: Payment info (required by law for payments)
- Your server: License keys (you control, can delete anytime)
- No Railway, no Heroku, no third-party databases

---

## Recommended Setup for You

Given your privacy requirements:

### For Testing (Now):
```bash
# Run on your Mac with ngrok
cd ~/multiagent-frameworks/tri-agent-system/monetization/backend
uvicorn stripe_integration:app --reload

# In another terminal:
ngrok http 8002
```

### For Production (When launching):

**Option A: Hetzner VPS** ($4.50/month)
- Full control
- EU-based (privacy-focused)
- Open source friendly

**Option B: Home Server + Cloudflare Tunnel** (Free)
- Mac always on at home
- Cloudflare tunnel (no port forwarding)
- Zero cost

Both options give you 100% control with no third-party data retention beyond Stripe (which is required for payment processing).

---

## What About Email?

When a purchase happens, you need to send the license key to the customer.

### Option 1: Stripe's Built-in Email (Simplest)

Stripe automatically sends receipt emails. You can customize them to include the license key.

**Configure in Stripe Dashboard:**
1. Settings → Emails → Receipts
2. Enable "Include custom message"
3. Add: "Your license key: {{metadata.license_key}}"

### Option 2: Self-Hosted Email (SMTP)

Use your own email server or Gmail SMTP:

```python
import smtplib
from email.mime.text import MIMEText

def _send_license_email(self, email: str, license_key: str, tier: str):
    msg = MIMEText(f"""
    Thank you for your purchase!

    License Key: {license_key}
    Tier: {tier}

    Activate: ./activate.sh
    """)

    msg['Subject'] = 'Your Double Down Studios License'
    msg['From'] = 'noreply@doubledownstudios.com'
    msg['To'] = email

    # Use Gmail SMTP (or your own mail server)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('your-email@gmail.com', 'your-app-password')
        smtp.send_message(msg)
```

---

## Summary

**You control everything:**
- ✅ Webhook server runs on YOUR hardware (Mac/VPS/home server)
- ✅ Licenses stored LOCALLY (JSON or SQLite on your machine)
- ✅ No Railway, no Heroku, no managed platforms
- ✅ 100% open source stack
- ✅ Only Stripe sees payment data (required for processing)

**Your costs:**
- $0 if running at home with Cloudflare Tunnel
- $4.50/month for Hetzner VPS (if you want dedicated server)
- ~2.9% Stripe fees per transaction (unavoidable for card payments)

The setup guide above shows how to run everything yourself with zero third-party data retention.
