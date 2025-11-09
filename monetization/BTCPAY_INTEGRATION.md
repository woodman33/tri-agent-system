# BTCPay Server Integration
## 100% Open Source, Self-Hosted Payment Processing

### What is BTCPay Server?

- **Truly open source**: Apache 2.0 license
- **Self-hosted**: Runs on your machine/VPS
- **Zero fees**: No middleman (only blockchain fees)
- **Privacy**: No KYC, no accounts
- **Payments**: Bitcoin, Lightning, altcoins

### Architecture

```
User → Your GitHub repo (clone free)
    ↓
User → "Buy Enterprise" button
    ↓
User → BTCPay invoice (your self-hosted server)
    ↓
User → Pays with Bitcoin/Lightning
    ↓
BTCPay → Webhook to your FastAPI
    ↓
Your server → Generates license
    ↓
Email → License key sent
```

**Data retention:**
- Your BTCPay instance only (you control)
- No Stripe, no third parties
- Blockchain transactions are public (nature of Bitcoin)

---

## Setup BTCPay Server

### Quick Start with Docker

```bash
# 1. Install BTCPay Server
git clone https://github.com/btcpayserver/btcpayserver-docker
cd btcpayserver-docker

# 2. Set environment variables
export BTCPAY_HOST="pay.doubledownstudios.com"
export NBITCOIN_NETWORK="mainnet"
export BTCPAYGEN_CRYPTO1="btc"
export BTCPAYGEN_LIGHTNING="clightning"

# 3. Run setup
. ./btcpay-setup.sh -i

# Your BTCPay runs at: https://pay.doubledownstudios.com
```

### Create Store & API Key

1. Go to your BTCPay dashboard
2. Create store: "Double Down Studios"
3. Settings → Access Tokens → Create new token
4. Permissions: `btcpay.store.canviewinvoices`, `btcpay.store.cancreateinvoice`
5. Copy API key

---

## Python Integration

### Install BTCPay Client

```bash
cd ~/multiagent-frameworks/tri-agent-system/monetization/backend
pip install btcpay
```

### Create `btcpay_integration.py`

```python
"""
BTCPay Server Integration for Double Down Studios
100% open source payment processing
"""
from btcpay import BTCPayClient
import os
import secrets
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
import json

# BTCPay configuration
BTCPAY_HOST = os.getenv('BTCPAY_HOST', 'https://pay.doubledownstudios.com')
BTCPAY_API_KEY = os.getenv('BTCPAY_API_KEY')

# Products
PRODUCTS = {
    'pro': {
        'name': 'Local AI Studio Pro',
        'price_usd': 9.99,
        'tier': 'pro',
        'addons': ['advanced-models']
    },
    'enterprise': {
        'name': 'Tri-Agent System',
        'price_usd': 39.99,
        'tier': 'enterprise',
        'addons': ['tri-agent-system', 'advanced-models', 'enterprise-features']
    }
}


class BTCPayPayments:
    """
    BTCPay payment integration for Double Down Studios.

    Features:
    - Bitcoin & Lightning payments
    - Self-hosted (no third parties)
    - Automatic license generation
    - Webhook handling
    """

    def __init__(self):
        if not BTCPAY_API_KEY:
            raise ValueError("BTCPAY_API_KEY environment variable not set")

        self.client = BTCPayClient(
            host=BTCPAY_HOST,
            pem=BTCPAY_API_KEY
        )

    def create_invoice(
        self,
        product_key: str,
        customer_email: str,
        redirect_url: str = "https://github.com/woodman33/tri-agent-system"
    ) -> Dict:
        """
        Create BTCPay invoice for payment.

        Args:
            product_key: 'pro' or 'enterprise'
            customer_email: Customer email for license delivery
            redirect_url: Where to redirect after payment

        Returns:
            {
                'invoice_id': str,
                'checkout_url': str,
                'btc_amount': float,
                'lightning_invoice': str
            }
        """
        if product_key not in PRODUCTS:
            raise ValueError(f"Unknown product: {product_key}")

        product = PRODUCTS[product_key]

        # Create invoice
        invoice = self.client.create_invoice({
            'price': product['price_usd'],
            'currency': 'USD',
            'orderId': f"{product_key}-{secrets.token_hex(8)}",
            'itemDesc': product['name'],
            'notificationEmail': customer_email,
            'redirectURL': redirect_url,
            'buyer': {
                'email': customer_email
            },
            'metadata': {
                'product_key': product_key,
                'tier': product['tier'],
                'customer_email': customer_email
            }
        })

        return {
            'invoice_id': invoice['id'],
            'checkout_url': invoice['url'],
            'btc_amount': invoice['btcPrice'],
            'lightning_invoice': invoice.get('lightningInvoice', '')
        }

    def handle_webhook(self, payload: Dict) -> Dict:
        """
        Handle BTCPay webhook events.

        Called when:
        - Invoice paid
        - Invoice confirmed
        - Invoice expired

        Returns:
            {
                'event_type': str,
                'license_key': str (if applicable),
                'customer_email': str,
                'product': str
            }
        """
        event_type = payload.get('type')
        invoice_data = payload.get('data', {})

        if event_type == 'InvoiceReceivedPayment':
            # Payment received, waiting for confirmations
            return {'event_type': 'payment_pending', 'handled': True}

        elif event_type == 'InvoicePaymentSettled':
            # Payment confirmed! Generate license
            return self._handle_payment_confirmed(invoice_data)

        elif event_type == 'InvoiceExpired':
            return {'event_type': 'invoice_expired', 'handled': True}

        return {'event_type': event_type, 'handled': False}

    def _handle_payment_confirmed(self, invoice_data: Dict) -> Dict:
        """
        Handle confirmed payment.
        Generate and save license key.
        """
        metadata = invoice_data.get('metadata', {})
        customer_email = metadata.get('customer_email')
        product_key = metadata.get('product_key')
        tier = metadata.get('tier')

        # Generate license key
        license_key = self._generate_license_key()

        # Save to database
        self._save_license(
            license_key=license_key,
            email=customer_email,
            tier=tier,
            product_key=product_key,
            invoice_id=invoice_data['id']
        )

        # Send license email
        self._send_license_email(customer_email, license_key, tier)

        return {
            'event_type': 'payment_confirmed',
            'license_key': license_key,
            'customer_email': customer_email,
            'tier': tier,
            'product_key': product_key
        }

    def _generate_license_key(self) -> str:
        """
        Generate unique license key.
        Format: XXXX-XXXX-XXXX-XXXX
        """
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        parts = []

        for _ in range(4):
            part = ''.join(secrets.choice(chars) for _ in range(4))
            parts.append(part)

        return '-'.join(parts)

    def _save_license(self, **kwargs):
        """
        Save license to local database.
        Stored only on YOUR machine.
        """
        license_db = Path.home() / '.doubledown-studios' / 'licenses.json'
        license_db.parent.mkdir(exist_ok=True)

        # Load existing
        if license_db.exists():
            with open(license_db) as f:
                licenses = json.load(f)
        else:
            licenses = {}

        # Add new license
        license_key = kwargs['license_key']
        licenses[license_key] = {
            **kwargs,
            'created_at': datetime.now().isoformat(),
            'valid': True,
            'payment_method': 'bitcoin'
        }

        # Save
        with open(license_db, 'w') as f:
            json.dump(licenses, f, indent=2)

        print(f"✅ License saved: {license_key}")

    def _send_license_email(self, email: str, license_key: str, tier: str):
        """
        Send license key via email.

        BTCPay can send emails automatically, or integrate with:
        - Your own SMTP server
        - Mailgun (self-hosted option available)
        """
        # BTCPay sends confirmation automatically
        # You can also send custom email here
        print(f"📧 Email to {email}:")
        print(f"   License Key: {license_key}")
        print(f"   Tier: {tier}")
        print(f"   Activation: ./activate.sh")

    def get_invoice_status(self, invoice_id: str) -> Dict:
        """Check invoice payment status"""
        invoice = self.client.get_invoice(invoice_id)

        return {
            'status': invoice['status'],
            'btc_paid': invoice.get('btcPaid', 0),
            'confirmed': invoice['status'] == 'confirmed'
        }


# FastAPI integration
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

app = FastAPI(title="Double Down Studios - BTCPay Integration")

btcpay = BTCPayPayments()


@app.post("/create-invoice/{product}")
async def create_invoice(
    product: str,
    email: Optional[str] = None
):
    """
    Create BTCPay invoice for payment.

    Usage:
        POST /create-invoice/pro?email=user@example.com
        POST /create-invoice/enterprise?email=user@example.com

    Returns Bitcoin payment details
    """
    try:
        result = btcpay.create_invoice(
            product_key=product,
            customer_email=email,
            redirect_url="https://github.com/woodman33/tri-agent-system"
        )

        return {
            'checkout_url': result['checkout_url'],
            'invoice_id': result['invoice_id'],
            'btc_amount': result['btc_amount']
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/webhooks/btcpay")
async def btcpay_webhook(request: Request):
    """
    BTCPay webhook endpoint.

    Configure in BTCPay Dashboard:
        URL: https://yourapi.com/webhooks/btcpay
        Events: InvoicePaymentSettled, InvoiceReceivedPayment
    """
    payload = await request.json()

    try:
        result = btcpay.handle_webhook(payload)
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/invoice/{invoice_id}")
async def check_invoice(invoice_id: str):
    """
    Check invoice payment status.
    Used by frontend to poll for payment confirmation.
    """
    status = btcpay.get_invoice_status(invoice_id)
    return status


# Example usage
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Double Down Studios - BTCPay Integration")
    print("=" * 60)
    print()

    # Demo: Create invoice
    payments = BTCPayPayments()

    print("Creating invoice for Enterprise tier...")
    result = payments.create_invoice(
        product_key='enterprise',
        customer_email='demo@example.com'
    )

    print(f"Checkout URL: {result['checkout_url']}")
    print(f"Invoice ID: {result['invoice_id']}")
    print(f"BTC Amount: {result['btc_amount']}")
    print()

    # Start server
    print("Starting webhook server...")
    print("Configure BTCPay webhook: https://yourapi.com/webhooks/btcpay")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8003)
```

---

## Frontend Integration

Update your React components to use BTCPay:

```jsx
// UpgradeBanner.jsx
const openPurchasePage = async () => {
  const apiUrl = 'https://your-api.com';
  const response = await fetch(`${apiUrl}/create-invoice/enterprise?email=user@example.com`);
  const data = await response.json();

  // Open BTCPay checkout
  window.open(data.checkout_url, '_blank');
};
```

---

## User Experience

**Purchase Flow:**

1. User clicks "Upgrade to Enterprise" → $39.99
2. BTCPay invoice opens → Shows BTC amount (e.g., 0.0005 BTC)
3. User pays with:
   - Bitcoin wallet (on-chain)
   - Lightning wallet (instant, low fees)
   - Mobile wallet (scan QR code)
4. Payment confirmed → Webhook fires
5. License generated → Email sent
6. User activates → Features unlock

**Payment Options:**
- Bitcoin (on-chain): 10-60 min confirmation
- Lightning Network: Instant, fees < $0.01
- Supports: Strike, Cash App, Phoenix, Muun, etc.

---

## Comparison

### BTCPay vs Stripe

| Feature | BTCPay | Stripe |
|---------|--------|--------|
| **Open Source** | ✅ Yes | ❌ No |
| **Self-Hosted** | ✅ Yes | ❌ No |
| **Fees** | ✅ None (blockchain only) | ❌ 2.9% + $0.30 |
| **Privacy** | ✅ No KYC | ❌ Requires identity |
| **Customer Base** | ⚠️ Smaller (crypto users) | ✅ Everyone |
| **Setup Complexity** | ⚠️ Higher | ✅ Easy |
| **Credit Cards** | ❌ No | ✅ Yes |

---

## Hybrid Approach

Offer BOTH payment methods:

```python
# In your app
def create_purchase_options(product_key: str):
    return {
        'btcpay': {
            'url': f'https://api.com/create-invoice/{product_key}',
            'label': 'Pay with Bitcoin',
            'fees': 'No fees',
            'time': '10-60 min'
        },
        'stripe': {
            'url': f'https://api.com/create-checkout/{product_key}',
            'label': 'Pay with Credit Card',
            'fees': '2.9%',
            'time': 'Instant'
        }
    }
```

Give users the choice!

---

## Costs

**BTCPay Server (Self-Hosted):**
- Software: Free (open source)
- VPS: $4.50/month (Hetzner)
- Bitcoin node: ~200GB storage
- Total: **~$5/month**

**Transaction Fees:**
- On-chain Bitcoin: $1-5 per transaction (varies)
- Lightning Network: <$0.01 per transaction
- **No percentage fees** like Stripe

**Your profit margin:**
- $39.99 sale via Stripe: You get $38.15 (2.9% fee)
- $39.99 sale via BTCPay: You get $39.99 (customer pays blockchain fee)

---

## Recommendation

### For Maximum Privacy & Open Source:
**Use BTCPay Server** exclusively
- 100% open source
- Self-hosted
- No third parties
- Zero fees

### For Maximum Sales:
**Offer both Stripe + BTCPay**
- Most customers prefer credit cards
- Crypto enthusiasts love BTCPay
- More payment options = more sales

### For Your Use Case:
Given your strong preference for open source, I recommend:
1. **Primary: BTCPay** for crypto payments
2. **Optional: Stripe** for credit cards (if you want wider audience)

You can start with BTCPay only and add Stripe later if needed.

---

## Setup Steps

```bash
# 1. Install BTCPay Server
git clone https://github.com/btcpayserver/btcpayserver-docker
cd btcpayserver-docker
. ./btcpay-setup.sh -i

# 2. Create Python integration
cd ~/multiagent-frameworks/tri-agent-system/monetization/backend
pip install btcpay

# 3. Configure environment
export BTCPAY_HOST="https://pay.doubledownstudios.com"
export BTCPAY_API_KEY="your-api-key"

# 4. Run server
uvicorn btcpay_integration:app --port 8003
```

**Your BTCPay server runs on YOUR hardware. Zero third parties.**
