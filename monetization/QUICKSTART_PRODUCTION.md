# Production Quick Start
## Get Double Down Studios Live in 30 Minutes

Follow these steps to launch your monetization system TODAY.

---

## Prerequisites

- [ ] Stripe account created
- [ ] Email for license delivery
- [ ] This Mac or a VPS

---

## 30-Minute Launch

### Step 1: Configure Environment (5 minutes)

```bash
cd ~/multiagent-frameworks/tri-agent-system/monetization/backend

# Copy example config
cp ../.env.example .env

# Edit with your keys
nano .env
```

**Minimum required (Stripe only):**
```bash
# Get from https://dashboard.stripe.com/test/apikeys
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET  # Add after Step 3

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your@email.com
SMTP_PASSWORD=your-app-password
```

### Step 2: Install & Test (5 minutes)

```bash
cd ~/multiagent-frameworks/tri-agent-system/monetization

# Install dependencies
pip install stripe fastapi uvicorn python-dotenv

# Or with Poetry
cd ~/multiagent-frameworks
poetry add stripe fastapi uvicorn python-dotenv

# Test locally
./deploy.sh local

# In browser: http://localhost:8004/health
# Should see: {"status": "healthy", "stripe_available": true}
```

### Step 3: Public Access with Ngrok (5 minutes)

```bash
# Install ngrok
brew install ngrok

# Create tunnel
ngrok http 8004

# Copy the HTTPS URL: https://abc123.ngrok.io
```

### Step 4: Configure Stripe Webhook (5 minutes)

1. Go to https://dashboard.stripe.com/test/webhooks
2. Click "Add endpoint"
3. **URL:** `https://abc123.ngrok.io/webhooks/stripe`
4. **Events:** Select `checkout.session.completed`
5. Click "Add endpoint"
6. Copy **Signing secret** (`whsec_...`)
7. Add to `.env`: `STRIPE_WEBHOOK_SECRET=whsec_...`
8. Restart server

### Step 5: Create Stripe Products (5 minutes)

1. Go to https://dashboard.stripe.com/test/products
2. Click "Add product"

**Product 1:**
- Name: `Local AI Studio Pro`
- Price: `$9.99` one-time
- Copy Price ID

**Product 2:**
- Name: `Tri-Agent System`
- Price: `$39.99` one-time
- Copy Price ID

3. Edit `backend/unified_payments.py`:
```python
PRODUCTS = {
    'pro': {
        'stripe_price_id': 'price_YOUR_PRO_ID_HERE',  # Paste here
        ...
    },
    'enterprise': {
        'stripe_price_id': 'price_YOUR_ENTERPRISE_ID_HERE',  # Paste here
        ...
    }
}
```

### Step 6: Test Purchase (5 minutes)

```bash
# Create test payment
curl -X POST "http://localhost:8004/create-payment/pro?payment_method=stripe&email=test@example.com"

# Returns: {"checkout_url": "https://checkout.stripe.com/..."}
# Open this URL in browser
```

**Use test card:**
- `4242 4242 4242 4242`
- Any future expiry, any CVC

**Verify:**
```bash
# Check license generated
cat ~/.doubledown-studios/licenses.json
```

---

## You're Live! 🎉

Your payment system is now accepting test payments.

### What Works Now:

✅ Stripe payments
✅ License generation
✅ Webhook processing
✅ Local license storage

### Next Steps:

1. **Add to your app:**
   - Import `PaymentMethodModal.jsx`
   - Show when user clicks "Upgrade"

2. **Go live:**
   - Switch to `sk_live_` keys in `.env`
   - Update webhook URL to production
   - Test with real card (small amount)
   - Launch! 🚀

---

## Production Deployment Options

### Option A: Keep Running on Mac

```bash
# Use Cloudflare Tunnel for permanent URL
brew install cloudflare/cloudflare/cloudflared
cloudflared tunnel login
cloudflared tunnel create doubledown-api

# Configure (see SELF_HOSTED_STRIPE.md)
```

### Option B: Deploy to VPS

```bash
# Generate systemd service
./deploy.sh vps

# Upload to VPS and install
scp -r backend your-vps:/opt/doubledown-studios/
ssh your-vps
# Follow printed instructions
```

---

## Monitoring

```bash
# Watch payments in real-time
tail -f ~/.doubledown-studios/logs/payments.log

# Check licenses
cat ~/.doubledown-studios/licenses.json

# API health
curl http://localhost:8004/health
```

---

## Troubleshooting

**"Payment failed"**
- Check Stripe Dashboard → Logs
- Verify test card: 4242 4242 4242 4242

**"Webhook not received"**
- Check ngrok is running
- Verify webhook URL in Stripe Dashboard
- Check server logs

**"License not generated"**
- Check webhook signature in `.env`
- Verify webhook fired (Stripe Dashboard → Webhooks)
- Check `~/.doubledown-studios/licenses.json` permissions

---

## Support

Full docs: `/monetization/PRODUCTION_CHECKLIST.md`

Need help? info@kraftforgelabs.com

---

**Time to launch:** 30 minutes ⏱️
**Status:** Production-ready ✅
**Next:** Add BTCPay for Bitcoin (optional)
