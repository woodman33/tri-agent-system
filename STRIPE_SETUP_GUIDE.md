# Stripe Integration Setup Guide
## Double Down Studios - Complete Stripe Setup

### Step 1: Create Stripe Account

1. Go to https://stripe.com
2. Sign up with your business email
3. Complete business verification
4. Get your API keys from Dashboard → Developers → API keys

### Step 2: Create Products in Stripe Dashboard

#### Product 1: Local AI Studio Pro

1. Go to Stripe Dashboard → Products
2. Click "Add product"
3. Fill in:
   - **Name:** Local AI Studio Pro
   - **Description:** Enhanced AI chat with 4 models, priority loading, custom themes
   - **Pricing:** One-time payment
   - **Price:** $9.99 USD
4. Click "Save product"
5. **Copy the Price ID** (looks like `price_1234567890abcdef`)
   - You'll need this for the code

#### Product 2: Tri-Agent System (Enterprise)

1. Click "Add product" again
2. Fill in:
   - **Name:** Tri-Agent System (Enterprise)
   - **Description:** 6-agent autonomous development system with Boyle's Law spawning
   - **Pricing:** One-time payment
   - **Price:** $39.99 USD
3. Click "Save product"
4. **Copy the Price ID**

### Step 3: Configure Your Code with Real Price IDs

Edit `/monetization/backend/stripe_integration.py`:

```python
# Replace these with your actual Stripe Price IDs
PRODUCTS = {
    'pro': {
        'price_id': 'price_YOUR_ACTUAL_PRO_PRICE_ID',  # Replace this
        'name': 'Local AI Studio Pro',
        'tier': 'pro',
        'addons': ['advanced-models']
    },
    'enterprise': {
        'price_id': 'price_YOUR_ACTUAL_ENTERPRISE_PRICE_ID',  # Replace this
        'name': 'Tri-Agent System',
        'tier': 'enterprise',
        'addons': ['tri-agent-system', 'advanced-models', 'enterprise-features']
    }
}
```

### Step 4: Set Up Environment Variables

Create `.env` file:

```bash
# Stripe API Keys (from Dashboard → Developers → API keys)
STRIPE_SECRET_KEY=sk_live_YOUR_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_PUBLISHABLE_KEY_HERE

# For testing, use test keys:
# STRIPE_SECRET_KEY=sk_test_YOUR_TEST_KEY_HERE
# STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_TEST_KEY_HERE
```

**IMPORTANT:** Never commit `.env` to GitHub!

Add to `.gitignore`:
```
.env
*.env
.env.*
```

### Step 5: Deploy Your Stripe Webhook Server

Your FastAPI server needs to be publicly accessible for Stripe webhooks.

#### Option A: Quick Deploy with Railway (Free Tier)

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `tri-agent-system` repo
5. Add environment variables:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET` (you'll get this in next step)
6. Railway gives you a URL like: `https://your-app.up.railway.app`

#### Option B: Deploy with Heroku

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create doubledown-studios-api

# Set environment variables
heroku config:set STRIPE_SECRET_KEY=sk_live_...

# Deploy
git push heroku main

# Your webhook URL: https://doubledown-studios-api.herokuapp.com/webhooks/stripe
```

#### Option C: Deploy with Fly.io (Free Tier)

```bash
# Install Fly CLI
brew install flyctl

# Login
fly auth login

# Launch app
fly launch

# Set secrets
fly secrets set STRIPE_SECRET_KEY=sk_live_...

# Your webhook URL: https://your-app.fly.dev/webhooks/stripe
```

### Step 6: Configure Stripe Webhooks

1. Go to Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Enter your webhook URL:
   - Railway: `https://your-app.up.railway.app/webhooks/stripe`
   - Heroku: `https://doubledown-studios-api.herokuapp.com/webhooks/stripe`
   - Fly.io: `https://your-app.fly.dev/webhooks/stripe`

4. Select events to listen for:
   - ✅ `checkout.session.completed`
   - ✅ `payment_intent.succeeded`
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.deleted`

5. Click "Add endpoint"

6. **Copy the Signing Secret** (looks like `whsec_...`)
   - Add this to your deployment:
     ```bash
     # Railway/Heroku/Fly.io
     STRIPE_WEBHOOK_SECRET=whsec_YOUR_SIGNING_SECRET
     ```

### Step 7: Test Your Integration

#### Test Mode (Safe Testing)

1. Use Stripe **test keys** (start with `sk_test_`)
2. Use test card: `4242 4242 4242 4242`
3. Test the full flow:
   ```bash
   # Start your local server
   cd monetization/backend
   uvicorn stripe_integration:app --reload

   # Visit in browser
   open http://localhost:8000/create-checkout/enterprise
   ```

4. Complete test purchase
5. Check webhook received
6. Verify license generated

#### Live Mode (Real Payments)

1. Switch to **live keys** (start with `sk_live_`)
2. Update webhook URL to production
3. Test with real card (charge yourself $0.50 to verify)
4. Refund test purchase in Stripe Dashboard

### Step 8: Update Frontend URLs

Edit your React components to use real Stripe checkout URLs:

**In `UpgradeBanner.jsx`:**
```javascript
const openPurchasePage = () => {
  // Replace with your deployed API URL
  const apiUrl = 'https://your-app.up.railway.app';
  window.open(`${apiUrl}/create-checkout/enterprise`, '_blank');
};
```

**In `FeatureLockedModal.jsx`:**
```javascript
const openPurchase = async (tier) => {
  const apiUrl = 'https://your-app.up.railway.app';
  const response = await fetch(`${apiUrl}/create-checkout/${tier}`);
  const data = await response.json();
  window.open(data.checkout_url, '_blank');
};
```

### Step 9: License Validation Setup

Your app needs to validate licenses against your server:

**In `LicenseActivationModal.jsx`:**
```javascript
const handleActivate = async () => {
  const apiUrl = 'https://your-app.up.railway.app';
  const response = await fetch(`${apiUrl}/api/license/activate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      license_key: licenseKey.trim().toUpperCase(),
      email: email.trim()
    })
  });
  // ... rest of activation logic
};
```

### Step 10: GitHub Repository Setup

#### Repo 1: local-ai-studio

```bash
# Create repo on GitHub
# Go to github.com/woodman33 → New repository
# Name: local-ai-studio
# Description: Professional local AI chat interface with vLLM
# Public repository

# Push your code
cd ~/local-ai-studio
git init
git add .
git commit -m "Initial commit: Local AI Studio with monetization"
git branch -M main
git remote add origin https://github.com/woodman33/local-ai-studio.git
git push -u origin main
```

#### Repo 2: tri-agent-system

```bash
# Create repo on GitHub
# Name: tri-agent-system
# Description: Autonomous 6-agent development system with Boyle's Law spawning
# Public repository

cd ~/multiagent-frameworks/tri-agent-system
git init
git add .
git commit -m "Initial commit: Tri-Agent System"
git branch -M main
git remote add origin https://github.com/woodman33/tri-agent-system.git
git push -u origin main
```

### Step 11: Add Purchase Links to README

**In `local-ai-studio/README.md`:**
```markdown
# Local AI Studio

Professional AI chat interface with local vLLM backend.

## Pricing

**Free Tier:**
- 2 AI models
- Basic chat interface
- 100% local processing

**Pro Tier - $9.99 (one-time):**
- 4 AI models
- Enhanced UI themes
- Priority loading
- [**Buy Pro →**](https://your-stripe-checkout-url)

**Enterprise Tier - $39.99 (one-time):**
- Everything in Pro
- Tri-Agent System addon
- 6 autonomous agents
- [**Buy Enterprise →**](https://your-stripe-checkout-url)
```

## Complete Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USERS (GitHub)                       │
│         github.com/woodman33/local-ai-studio            │
│         github.com/woodman33/tri-agent-system           │
└────────────────────┬────────────────────────────────────┘
                     │ Clone repos (free)
                     │
                     ▼
         ┌───────────────────────────┐
         │   Free Tier Running       │
         │   (2 models available)    │
         └───────────┬───────────────┘
                     │
                     │ Click "Upgrade"
                     ▼
         ┌───────────────────────────┐
         │  Your Stripe Checkout      │
         │  (hosted by Stripe)        │
         └───────────┬───────────────┘
                     │
                     │ Payment successful
                     ▼
         ┌───────────────────────────┐
         │  Stripe Webhook            │
         │  → Your Railway/Heroku API │
         └───────────┬───────────────┘
                     │
                     │ Generate license
                     ▼
         ┌───────────────────────────┐
         │  Email to customer         │
         │  License: XXXX-XXXX-...    │
         └───────────┬───────────────┘
                     │
                     │ User enters license
                     ▼
         ┌───────────────────────────┐
         │  App validates license     │
         │  Downloads tri-agent addon │
         │  Features unlock           │
         └───────────────────────────┘
```

## Security Checklist

- [ ] Never commit `.env` files
- [ ] Use environment variables for all secrets
- [ ] Add `.env` to `.gitignore`
- [ ] Use Stripe test mode during development
- [ ] Verify webhook signatures
- [ ] Use HTTPS for all webhook endpoints
- [ ] Store license keys securely
- [ ] Validate license keys server-side

## Monitoring & Analytics

**Stripe Dashboard shows:**
- Total revenue
- Number of purchases
- Customer emails
- Refund requests
- Failed payments

**Your API logs show:**
- License activations
- Addon downloads
- Feature usage
- Error rates

## Support & Refunds

**Handle in Stripe Dashboard:**
- Refunds: Dashboard → Payments → Refund
- Customer emails: Automatically captured
- Invoice history: Dashboard → Payments

**Customer support email:**
- Set up: support@doubledownstudios.com
- Forward to your personal email
- Use Gmail or custom domain

## Next Steps

1. ✅ Create Stripe account
2. ✅ Create two products ($9.99, $39.99)
3. ✅ Copy Price IDs to code
4. ✅ Deploy API server (Railway/Heroku/Fly.io)
5. ✅ Configure Stripe webhooks
6. ✅ Test with test cards
7. ✅ Push code to GitHub repos
8. ✅ Add purchase links to README
9. ✅ Go live with real keys
10. ✅ Launch! 🚀

## FAQ

**Q: Do I need GitHub Marketplace?**
A: No. GitHub is just for hosting code. Stripe handles payments.

**Q: What fees will I pay?**
A: Stripe charges ~2.9% + $0.30 per transaction. No monthly fees.

**Q: How do users get the code?**
A: They clone from GitHub (free), then purchase license to unlock features.

**Q: What if someone pirates the license key?**
A: License keys are tied to email + optional hardware ID for security.

**Q: Can I change prices later?**
A: Yes, just create new Price IDs in Stripe and update your code.

---

**Ready to launch Double Down Studios!** 🎲
