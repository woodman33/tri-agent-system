# Production Launch Checklist
## Double Down Studios - Go-Live Guide

Complete these steps to launch your monetization system.

---

## Phase 1: Initial Setup (1-2 hours)

### Step 1: Create Stripe Account

- [ ] Go to https://stripe.com
- [ ] Sign up with business email
- [ ] Complete identity verification
- [ ] Add bank account for payouts
- [ ] Set business name: "Double Down Studios"

### Step 2: Create Stripe Products

**In Stripe Dashboard → Products → Create Product:**

- [ ] **Product 1: Local AI Studio Pro**
  - Name: `Local AI Studio Pro`
  - Price: `$9.99`
  - Type: One-time payment
  - Copy Price ID: `price_________________`

- [ ] **Product 2: Tri-Agent System**
  - Name: `Tri-Agent System (Enterprise)`
  - Price: `$39.99`
  - Type: One-time payment
  - Copy Price ID: `price_________________`

### Step 3: Configure Environment

```bash
cd ~/multiagent-frameworks/tri-agent-system/monetization/backend

# Copy example environment file
cp ../.env.example .env

# Edit with your keys
nano .env  # or vim, code, etc.
```

**Fill in these values:**
```bash
# From Stripe Dashboard → Developers → API keys
STRIPE_SECRET_KEY=sk_test_________________  # Start with test mode

# From Stripe Dashboard → Developers → Webhooks (after Step 6)
STRIPE_WEBHOOK_SECRET=whsec_________________

# BTCPay (if using Bitcoin payments - optional for now)
BTCPAY_HOST=https://pay.doubledownstudios.com
BTCPAY_API_KEY=_________________

# Email (for sending license keys)
SMTP_SERVER=smtp.gmail.com
SMTP_USER=info@kraftforgelabs.com
SMTP_PASSWORD=_________________  # Gmail app password
```

---

## Phase 2: Testing (30 minutes)

### Step 4: Test Locally

```bash
cd ~/multiagent-frameworks/tri-agent-system/monetization

# Run deployment script in local mode
./deploy.sh local

# Server starts at http://localhost:8004
```

**Test endpoints:**
```bash
# Check health
curl http://localhost:8004/health

# Check payment methods
curl http://localhost:8004/payment-methods
```

### Step 5: Test with Ngrok

```bash
# In another terminal, start ngrok
ngrok http 8004

# Copy the https URL: https://abc123.ngrok.io
```

**Or use deploy script:**
```bash
./deploy.sh test  # Automatically starts ngrok
```

### Step 6: Configure Stripe Test Webhooks

**In Stripe Dashboard → Developers → Webhooks:**

- [ ] Click "Add endpoint"
- [ ] **Endpoint URL:** `https://abc123.ngrok.io/webhooks/stripe` (your ngrok URL)
- [ ] **Events to send:**
  - [x] `checkout.session.completed`
- [ ] Click "Add endpoint"
- [ ] Copy **Signing secret** (`whsec_...`)
- [ ] Add to `.env`: `STRIPE_WEBHOOK_SECRET=whsec_...`
- [ ] Restart server: `./deploy.sh test`

### Step 7: Complete Test Purchase

```bash
# Create test payment
curl -X POST "http://localhost:8004/create-payment/pro?payment_method=stripe&email=test@example.com"

# Returns checkout URL - open in browser
```

**Use Stripe test card:**
- Card number: `4242 4242 4242 4242`
- Expiry: Any future date
- CVC: Any 3 digits
- ZIP: Any 5 digits

**Verify:**
- [ ] Payment completes successfully
- [ ] Webhook fires to your server
- [ ] License key generated in `~/.doubledown-studios/licenses.json`
- [ ] Check logs for any errors

---

## Phase 3: BTCPay Setup (Optional - 1-2 hours)

Skip this if you only want to accept credit cards for now.

### Step 8: Install BTCPay Server

**Option A: Docker on VPS (Recommended)**

```bash
# SSH into your VPS
ssh root@your-server-ip

# Clone BTCPay
git clone https://github.com/btcpayserver/btcpayserver-docker
cd btcpayserver-docker

# Configure
export BTCPAY_HOST="pay.doubledownstudios.com"
export NBITCOIN_NETWORK="mainnet"
export BTCPAYGEN_CRYPTO1="btc"
export BTCPAYGEN_LIGHTNING="clightning"
export LETSENCRYPT_EMAIL="your@email.com"

# Install
. ./btcpay-setup.sh -i
```

**Option B: Use Testnet First**

```bash
export NBITCOIN_NETWORK="testnet"  # Safe testing
```

### Step 9: Configure BTCPay

- [ ] Access BTCPay at `https://pay.doubledownstudios.com`
- [ ] Create admin account
- [ ] Create store: "Double Down Studios"
- [ ] Set default currency: USD
- [ ] Configure Lightning Network (optional but recommended)
- [ ] Go to Account → API Keys → Generate Key
- [ ] Permissions: `btcpay.store.canviewinvoices`, `btcpay.store.cancreateinvoice`
- [ ] Copy API key
- [ ] Add to `.env`: `BTCPAY_API_KEY=...`

### Step 10: Configure BTCPay Webhook

- [ ] In BTCPay → Store → Settings → Webhooks
- [ ] Click "Create Webhook"
- [ ] **URL:** `https://your-api.com/webhooks/btcpay`
- [ ] **Events:** `InvoicePaymentSettled`, `InvoiceReceivedPayment`
- [ ] Save webhook

### Step 11: Test Bitcoin Payment

```bash
# Create BTCPay test payment
curl -X POST "http://localhost:8004/create-payment/pro?payment_method=btcpay&email=test@example.com"

# Open checkout URL in browser
# Pay with testnet Bitcoin or use BTCPay test mode
```

---

## Phase 4: Production Deployment (1 hour)

### Step 12: Choose Deployment Method

**Option A: Run on Your Mac (Simplest)**

```bash
# Keep server running 24/7
./deploy.sh local

# Use Cloudflare Tunnel for public access (free)
brew install cloudflare/cloudflare/cloudflared
cloudflared tunnel login
cloudflared tunnel create doubledown-api
# Follow setup in SELF_HOSTED_STRIPE.md
```

**Option B: Deploy to VPS (Recommended for Production)**

```bash
# Generate systemd service
./deploy.sh vps

# Follow printed instructions to:
# 1. Upload to VPS
# 2. Install systemd service
# 3. Start service
```

**VPS Options:**
- Hetzner: €4.15/month
- DigitalOcean: $6/month
- Linode: $5/month
- Oracle Cloud: Free tier available

### Step 13: Set Up Domain & SSL

```bash
# On your VPS, install Nginx + Certbot
apt update
apt install -y nginx certbot python3-certbot-nginx

# Configure Nginx reverse proxy
cat > /etc/nginx/sites-available/doubledown-api << 'EOF'
server {
    listen 80;
    server_name api.doubledownstudios.com;

    location / {
        proxy_pass http://127.0.0.1:8004;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/doubledown-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Get free SSL certificate
certbot --nginx -d api.doubledownstudios.com
```

### Step 14: Update Production Webhooks

**Stripe:**
- [ ] Dashboard → Developers → Webhooks
- [ ] Update endpoint URL: `https://api.doubledownstudios.com/webhooks/stripe`
- [ ] Or add new endpoint for production (keep test endpoint separate)

**BTCPay:**
- [ ] Store → Settings → Webhooks
- [ ] Update URL: `https://api.doubledownstudios.com/webhooks/btcpay`

---

## Phase 5: Go Live (30 minutes)

### Step 15: Switch to Live Keys

```bash
# Edit .env
nano ~/monetization/backend/.env

# Change from test to live keys
STRIPE_SECRET_KEY=sk_live_________________  # Not sk_test_
STRIPE_WEBHOOK_SECRET=whsec_________________  # From live webhook

# Restart server
sudo systemctl restart doubledown-api
```

### Step 16: Test Live Payment

**IMPORTANT: Test with small amount first**

- [ ] Create payment for Pro tier ($9.99)
- [ ] Use your own credit card
- [ ] Complete purchase
- [ ] Verify license generated
- [ ] Test activation in app
- [ ] Refund yourself in Stripe Dashboard

### Step 17: Monitor First Sales

```bash
# Watch logs in real-time
tail -f ~/.doubledown-studios/logs/payments.log

# Or with systemd
sudo journalctl -u doubledown-api -f

# Check licenses
cat ~/.doubledown-studios/licenses.json
```

---

## Phase 6: GitHub Repositories (1 hour)

### Step 18: Create GitHub Repos

**Repo 1: local-ai-studio**

```bash
# On GitHub.com
# 1. Go to github.com/woodman33
# 2. Click "New repository"
# 3. Name: local-ai-studio
# 4. Description: Professional local AI chat interface with vLLM
# 5. Public repository
# 6. Create

# On your Mac
cd ~/local-ai-studio  # Your existing project
git init
git add .
git commit -m "Initial commit: Local AI Studio v1.0"
git branch -M main
git remote add origin https://github.com/woodman33/local-ai-studio.git
git push -u origin main
```

**Repo 2: tri-agent-system**

```bash
cd ~/multiagent-frameworks/tri-agent-system
git init
git add .
git commit -m "Initial commit: Tri-Agent System v1.0"
git branch -M main
git remote add origin https://github.com/woodman33/tri-agent-system.git
git push -u origin main
```

### Step 19: Update README Files

- [ ] Add purchase links to README
- [ ] Add feature comparison tables
- [ ] Add installation instructions
- [ ] Add license activation guide
- [ ] Add screenshots/demos

### Step 20: Add GitHub Funding File

```bash
# In both repos
mkdir -p .github
cat > .github/FUNDING.yml << 'EOF'
custom: ["https://api.doubledownstudios.com/create-payment/enterprise"]
EOF

git add .github/FUNDING.yml
git commit -m "Add GitHub funding links"
git push
```

---

## Phase 7: Launch (Now!)

### Step 21: Final Checks

- [ ] All webhooks configured and tested
- [ ] Live payments work end-to-end
- [ ] License activation works in app
- [ ] Email delivery working
- [ ] Error monitoring in place
- [ ] Backup system for licenses
- [ ] Documentation complete

### Step 22: Announce Launch

**Share on:**
- [ ] Twitter/X
- [ ] Reddit (r/selfhosted, r/LocalLLaMA)
- [ ] Hacker News
- [ ] Product Hunt (optional)
- [ ] Your email list

**Launch message template:**
```
🚀 Launching Double Down Studios!

Two new products for privacy-focused AI developers:

🎨 Local AI Studio Pro ($9.99)
- 4 local AI models
- Enhanced UI
- Priority loading

🤖 Tri-Agent System ($39.99)
- 6 autonomous agents
- Boyle's Law spawning
- 100% local processing

✅ One-time purchase (no subscription)
✅ Lifetime updates
✅ 30-day money-back guarantee

Choose payment method:
💳 Credit card (Stripe)
₿ Bitcoin/Lightning (BTCPay)

GitHub: github.com/woodman33
```

---

## Post-Launch Monitoring

### Daily Checks (First Week)

- [ ] Check payment success rate
- [ ] Monitor webhook delivery
- [ ] Review error logs
- [ ] Respond to customer emails
- [ ] Check license activation rate

### Weekly Tasks

- [ ] Backup license database
- [ ] Review sales metrics
- [ ] Update documentation
- [ ] Process refund requests (if any)
- [ ] Gather customer feedback

### Monthly Tasks

- [ ] Rotate API keys (security)
- [ ] Review payment method usage (Stripe vs BTCPay)
- [ ] Analyze conversion rates
- [ ] Plan feature updates
- [ ] Financial reporting

---

## Success Metrics

**Week 1 Goals:**
- [ ] 10+ GitHub stars
- [ ] 2-5 purchases
- [ ] Zero critical errors
- [ ] <24hr support response time

**Month 1 Goals:**
- [ ] 100+ GitHub stars
- [ ] 10+ Pro purchases
- [ ] 2+ Enterprise purchases
- [ ] Positive user feedback
- [ ] $200+ revenue

**Month 3 Goals:**
- [ ] 500+ GitHub stars
- [ ] 50+ Pro purchases
- [ ] 10+ Enterprise purchases
- [ ] ~$1,000 revenue
- [ ] Feature requests implemented

---

## Troubleshooting

### Payments Not Working

```bash
# Check server status
curl https://api.doubledownstudios.com/health

# Check logs
tail -f ~/.doubledown-studios/logs/payments.log

# Verify webhooks
# Stripe Dashboard → Webhooks → View attempts
# BTCPay Dashboard → Store → Webhooks → Delivery logs
```

### Webhooks Not Firing

- [ ] Check webhook URL is correct
- [ ] Verify SSL certificate is valid
- [ ] Check firewall allows incoming HTTPS
- [ ] Test webhook manually in dashboard

### License Not Generated

- [ ] Check webhook received successfully
- [ ] Verify payment actually completed
- [ ] Check license database permissions
- [ ] Review server error logs

---

## Support

### For Development Issues

- Documentation: `/monetization/DUAL_PAYMENT_SETUP.md`
- Stripe Docs: https://stripe.com/docs
- BTCPay Docs: https://docs.btcpayserver.org

### For Customer Issues

- Email: info@kraftforgelabs.com
- GitHub Issues: Enable on both repos
- Response time goal: <24 hours

---

## You're Ready to Launch! 🚀

**Current Status:**
- ✅ Complete payment system built
- ✅ Dual payment methods (Stripe + BTCPay)
- ✅ License management system
- ✅ Frontend components
- ✅ Documentation
- ✅ Deployment scripts

**Next Step:** Work through this checklist top to bottom.

**Estimated time to launch:** 4-6 hours

**Good luck with your launch! 🎲**

---

Double Down Studios - Production Checklist
Last updated: 2025
