# Dual Payment System Setup Guide
## Stripe + BTCPay Integration for Double Down Studios

Give customers the choice: Credit cards OR Bitcoin/Lightning.

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│           Customer Choice                    │
│                                              │
│  ┌────────────┐           ┌──────────────┐  │
│  │ 💳 Stripe  │    OR     │ ₿ BTCPay     │  │
│  │ (Cards)    │           │ (Crypto)     │  │
│  └────────────┘           └──────────────┘  │
└─────────────────────────────────────────────┘
           │                        │
           ▼                        ▼
    ┌──────────┐            ┌──────────────┐
    │  Stripe  │            │  YOUR VPS    │
    │  Hosted  │            │  BTCPay      │
    └────┬─────┘            └──────┬───────┘
         │                         │
         │    Webhooks to YOUR API │
         └─────────────┬───────────┘
                       ▼
              ┌────────────────────┐
              │  Your FastAPI      │
              │  unified_payments  │
              └─────────┬──────────┘
                        │
                        ▼
              License Generated Locally
              Stored: ~/.doubledown-studios/
```

**Data Retention:**
- Stripe: Payment info (required by law)
- BTCPay: Runs on YOUR server (you control)
- Licenses: Stored LOCALLY on your machine
- No third-party databases

---

## Step 1: Environment Setup

### Install Dependencies

```bash
cd ~/multiagent-frameworks/tri-agent-system/monetization/backend

# Python dependencies
pip install stripe btcpay fastapi uvicorn python-dotenv

# Or with Poetry (if using multiagent-frameworks environment)
cd ~/multiagent-frameworks
poetry add stripe btcpay fastapi uvicorn python-dotenv
```

### Create .env File

```bash
cat > .env << 'EOF'
# Stripe Configuration (use test keys for testing)
STRIPE_SECRET_KEY=sk_test_YOUR_TEST_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE

# BTCPay Configuration
BTCPAY_HOST=https://pay.doubledownstudios.com
BTCPAY_API_KEY=YOUR_BTCPAY_API_KEY_HERE

# Email Configuration (optional, for sending license keys)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=info@kraftforgelabs.com
SMTP_PASSWORD=your-app-password
EOF

# IMPORTANT: Never commit .env to git
echo ".env" >> .gitignore
```

---

## Step 2: Stripe Setup (Credit Cards)

### A. Create Stripe Account

1. Go to https://stripe.com
2. Sign up for account
3. Complete business verification

### B. Create Products

**In Stripe Dashboard → Products:**

1. **Product 1: Local AI Studio Pro**
   - Name: `Local AI Studio Pro`
   - Price: `$9.99` one-time
   - Copy **Price ID** (e.g., `price_1ABC123...`)

2. **Product 2: Tri-Agent System**
   - Name: `Tri-Agent System (Enterprise)`
   - Price: `$39.99` one-time
   - Copy **Price ID** (e.g., `price_1XYZ789...`)

### C. Update Code with Price IDs

Edit `unified_payments.py`:

```python
PRODUCTS = {
    'pro': {
        'name': 'Local AI Studio Pro',
        'price_usd': 9.99,
        'stripe_price_id': 'price_YOUR_ACTUAL_PRO_PRICE_ID',  # ← Paste here
        'tier': 'pro',
        'addons': ['advanced-models']
    },
    'enterprise': {
        'name': 'Tri-Agent System',
        'price_usd': 39.99,
        'stripe_price_id': 'price_YOUR_ACTUAL_ENTERPRISE_PRICE_ID',  # ← Paste here
        'tier': 'enterprise',
        'addons': ['tri-agent-system', 'advanced-models', 'enterprise-features']
    }
}
```

### D. Get API Keys

**In Stripe Dashboard → Developers → API keys:**

1. **For Testing:**
   - Copy `Publishable key` (starts with `pk_test_`)
   - Copy `Secret key` (starts with `sk_test_`)

2. **For Production:**
   - Switch to "Live mode"
   - Copy `Publishable key` (starts with `pk_live_`)
   - Copy `Secret key` (starts with `sk_live_`)

Add to `.env`:
```bash
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE  # Or sk_live_ for production
```

### E. Configure Webhooks

**In Stripe Dashboard → Developers → Webhooks:**

1. Click "Add endpoint"
2. **Endpoint URL:** `https://your-api.com/webhooks/stripe`
3. **Events to listen for:**
   - ✅ `checkout.session.completed`
4. Click "Add endpoint"
5. Copy **Signing secret** (starts with `whsec_`)

Add to `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SIGNING_SECRET_HERE
```

---

## Step 3: BTCPay Setup (Bitcoin/Lightning)

### A. Install BTCPay Server

**Option 1: Docker Install (Recommended)**

```bash
# Clone BTCPay
git clone https://github.com/btcpayserver/btcpayserver-docker
cd btcpayserver-docker

# Configure
export BTCPAY_HOST="pay.doubledownstudios.com"
export NBITCOIN_NETWORK="mainnet"  # Or "testnet" for testing
export BTCPAYGEN_CRYPTO1="btc"
export BTCPAYGEN_LIGHTNING="clightning"  # Lightning Network support
export BTCPAYGEN_REVERSEPROXY="nginx"
export LETSENCRYPT_EMAIL="your@email.com"

# Run setup
. ./btcpay-setup.sh -i

# BTCPay will be available at: https://pay.doubledownstudios.com
```

**Option 2: Use Free BTCPay Hosting (Testing Only)**

For testing, you can use a third-party host:
- https://mainnet.demo.btcpayserver.org
- https://testnet.demo.btcpayserver.org

**⚠️ For production, ALWAYS self-host for privacy.**

### B. Create Store

1. Go to your BTCPay dashboard
2. Click "Stores" → "Create a new store"
3. **Store Name:** `Double Down Studios`
4. **Default Currency:** `USD`
5. Click "Create"

### C. Configure Lightning Network (Optional but Recommended)

Lightning payments are instant and have fees < $0.01.

1. In your store → Settings → Lightning
2. Enable Lightning
3. Connection string: Auto-configured if using Docker setup

### D. Create API Key

1. Go to Account → API Keys
2. Click "Generate Key"
3. **Permissions needed:**
   - ✅ `btcpay.store.canviewinvoices`
   - ✅ `btcpay.store.cancreateinvoice`
   - ✅ `btcpay.store.webhooks.canmodifywebhooks`
4. Click "Generate"
5. Copy the API key

Add to `.env`:
```bash
BTCPAY_HOST=https://pay.doubledownstudios.com
BTCPAY_API_KEY=YOUR_BTCPAY_API_KEY_HERE
```

### E. Configure Webhooks

1. In BTCPay → Store → Settings → Webhooks
2. Click "Create Webhook"
3. **Payload URL:** `https://your-api.com/webhooks/btcpay`
4. **Events:**
   - ✅ `InvoicePaymentSettled`
   - ✅ `InvoiceReceivedPayment`
5. Click "Create"

---

## Step 4: Run Your Unified Payment Server

### A. Start the Server

```bash
cd ~/multiagent-frameworks/tri-agent-system/monetization/backend

# Load environment variables
source .env

# Run with uvicorn
uvicorn unified_payments:app --host 0.0.0.0 --port 8004 --reload

# Server running at: http://localhost:8004
```

### B. Test Endpoints

```bash
# Check health and available payment methods
curl http://localhost:8004/health
curl http://localhost:8004/payment-methods

# Should return:
# {
#   "stripe": {...},
#   "btcpay": {...}
# }
```

### C. Make Server Public

For webhooks to work, your server must be publicly accessible.

**Option 1: Ngrok (Testing)**

```bash
# Install ngrok
brew install ngrok

# Tunnel to your local server
ngrok http 8004

# Ngrok gives you: https://abc123.ngrok.io
# Update webhooks to use this URL
```

**Option 2: Self-Hosted VPS (Production)**

Deploy to Hetzner, DigitalOcean, or home server:

```bash
# SSH into your server
ssh root@your-server-ip

# Upload your code
scp -r monetization/backend root@your-server-ip:/opt/doubledown-studios/

# Set up systemd service (see SELF_HOSTED_STRIPE.md for details)

# Your API will be at: https://api.doubledownstudios.com
```

**Option 3: Cloudflare Tunnel (Free)**

```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared

# Login
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create doubledown-api

# Run tunnel (see SELF_HOSTED_STRIPE.md for full config)
cloudflared tunnel run doubledown-api
```

---

## Step 5: Frontend Integration

### Update Your React App

```jsx
import { PaymentMethodModal } from './PaymentMethodModal';

function YourApp() {
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  return (
    <>
      <button onClick={() => setShowPaymentModal(true)}>
        Upgrade to Enterprise - $39.99
      </button>

      {showPaymentModal && (
        <PaymentMethodModal
          product="enterprise"  // or "pro"
          onClose={() => setShowPaymentModal(false)}
        />
      )}
    </>
  );
}
```

The `PaymentMethodModal` component will:
1. Fetch available payment methods from your API
2. Show customer the choice: Stripe or BTCPay
3. Create payment with their chosen method
4. Open checkout in new window

---

## Step 6: Test Full Flow

### Test with Stripe (Test Mode)

1. Use test API keys (`sk_test_...`)
2. Create payment via frontend
3. Use test card: `4242 4242 4242 4242`
4. Expiry: Any future date
5. CVC: Any 3 digits
6. Webhook should fire → License generated

### Test with BTCPay (Testnet)

1. Use testnet BTCPay instance
2. Create payment via frontend
3. Pay with testnet Bitcoin wallet
4. Or use BTCPay's test mode (no real Bitcoin needed)
5. Webhook should fire → License generated

---

## Step 7: Go Live

### A. Switch to Production Keys

**Stripe:**
```bash
# In .env, switch from sk_test_ to sk_live_
STRIPE_SECRET_KEY=sk_live_YOUR_LIVE_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_LIVE_SECRET
```

**BTCPay:**
```bash
# Switch from testnet to mainnet
NBITCOIN_NETWORK="mainnet"
```

### B. Update Webhooks

Point webhooks to your production URL:
- Stripe webhook: `https://api.doubledownstudios.com/webhooks/stripe`
- BTCPay webhook: `https://api.doubledownstudios.com/webhooks/btcpay`

### C. Test with Small Amount

1. Purchase Pro tier ($9.99) with your own card/Bitcoin
2. Verify license generated
3. Test activation flow
4. Refund yourself in Stripe Dashboard

---

## Customer Experience

### Purchase Flow (Credit Card)

1. User clicks "Upgrade to Enterprise"
2. Modal shows: **Credit Card** or Bitcoin
3. User selects "Credit or Debit Card"
4. Enters email
5. Clicks "Pay with Card"
6. Stripe checkout opens → Complete payment
7. Email arrives with license key: `XXXX-XXXX-XXXX-XXXX`
8. User enters key in app → Features unlock

### Purchase Flow (Bitcoin)

1. User clicks "Upgrade to Enterprise"
2. Modal shows: Credit Card or **Bitcoin**
3. User selects "Bitcoin / Lightning Network"
4. Enters email
5. Clicks "Pay with Bitcoin"
6. BTCPay invoice opens → Shows QR code + BTC amount
7. User scans with wallet → Pays
8. **Lightning:** Instant confirmation
9. **Bitcoin:** 10-60 min for confirmations
10. Email arrives with license key
11. User enters key in app → Features unlock

---

## Comparison Table

| Feature | Stripe (Credit Cards) | BTCPay (Bitcoin/Lightning) |
|---------|----------------------|---------------------------|
| **Fees** | 2.9% + $0.30 per transaction | None (customer pays blockchain fee) |
| **Processing** | Instant | Lightning: Instant<br>Bitcoin: 10-60 min |
| **Privacy** | KYC required | No KYC |
| **Open Source** | No (hosted service) | Yes (you host it) |
| **Setup** | Easy | Moderate |
| **Customer Base** | Everyone | Crypto users (~5-10% of market) |
| **Your Cut (on $39.99)** | $38.15 | $39.99 |
| **Data Retention** | Stripe stores payment info | You control everything |

---

## Recommended Strategy

### Month 1-3: Both Methods

Offer both payment methods and see which customers prefer:
- Track: How many choose Stripe vs BTCPay
- Track: Conversion rates for each method
- Track: Support requests for each method

### Month 4+: Optimize

If 90%+ choose Stripe → Keep both but prioritize Stripe in UI
If 20%+ choose BTCPay → Promote it more (privacy angle)

**Expected split:** ~90% Stripe, ~10% BTCPay (based on crypto adoption)

---

## Costs

### Stripe
- **Setup:** Free
- **Per transaction:** 2.9% + $0.30
- **Monthly:** $0 (no subscription)

### BTCPay
- **Setup:** Free (open source)
- **VPS hosting:** $4.50/month (Hetzner)
- **Per transaction:** $0 fees to you
- **Customer pays:** $0.01 (Lightning) or $1-5 (Bitcoin on-chain)

### Total Monthly Costs

**If self-hosting:**
- VPS for API + BTCPay: $4.50/month
- Domain: $1/month ($12/year)
- SSL: $0 (Let's Encrypt)
- **Total: ~$5.50/month**

**Plus per-transaction:**
- Stripe fees: 2.9% + $0.30 per sale

---

## Security Checklist

- [ ] Never commit `.env` to git
- [ ] Add `.env` to `.gitignore`
- [ ] Use HTTPS for all webhook endpoints
- [ ] Verify webhook signatures (Stripe)
- [ ] Store licenses locally only
- [ ] Use strong passwords for BTCPay admin
- [ ] Enable 2FA on Stripe account
- [ ] Regularly backup license database
- [ ] Monitor webhook failures
- [ ] Set up error alerting

---

## Monitoring

### Check Payment System Health

```bash
curl https://api.doubledownstudios.com/health

# Returns:
# {
#   "status": "healthy",
#   "stripe_available": true,
#   "btcpay_available": true
# }
```

### View Available Methods

```bash
curl https://api.doubledownstudios.com/payment-methods

# Returns details about Stripe and BTCPay options
```

### Check Licenses

```bash
cat ~/.doubledown-studios/licenses.json

# Shows all generated licenses with payment method
```

---

## Support & Troubleshooting

### Stripe Issues

- **"Invalid API key":** Check `.env` has correct `sk_test_` or `sk_live_` key
- **"Webhook signature failed":** Update `STRIPE_WEBHOOK_SECRET` from dashboard
- **"Price not found":** Update `stripe_price_id` in `PRODUCTS` dict

### BTCPay Issues

- **"Connection failed":** Check `BTCPAY_HOST` is correct
- **"Invalid API key":** Regenerate key in BTCPay dashboard
- **"Invoice not created":** Check store is configured with Bitcoin wallet

### License Issues

- **"License not saved":** Check permissions on `~/.doubledown-studios/`
- **"Email not sent":** Configure SMTP settings in `.env`

---

## Next Steps

1. ✅ Set up both Stripe and BTCPay accounts
2. ✅ Configure products and webhooks
3. ✅ Deploy unified payment server
4. ✅ Test with test cards and testnet Bitcoin
5. ✅ Integrate frontend modal
6. ✅ Go live with production keys
7. ✅ Monitor sales and payment method preferences

**You now have a complete dual-payment system that gives customers choice while maintaining privacy options!**

---

Copyright © 2025 Double Down Studios
Payment integration code MIT licensed.
