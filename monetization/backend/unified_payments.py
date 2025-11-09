"""
Unified Payment System for Double Down Studios
Supports BOTH Stripe (credit cards) and BTCPay (Bitcoin/Lightning)

Customer chooses their preferred payment method.
"""
import stripe
import os
import secrets
import json
from datetime import datetime
from typing import Dict, Optional, Literal
from pathlib import Path

# Stripe configuration (minimal, privacy-focused usage)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# BTCPay configuration (100% open source)
BTCPAY_HOST = os.getenv('BTCPAY_HOST', 'https://pay.doubledownstudios.com')
BTCPAY_API_KEY = os.getenv('BTCPAY_API_KEY')

# Products (same for both payment methods)
PRODUCTS = {
    'pro': {
        'name': 'Local AI Studio Pro',
        'price_usd': 9.99,
        'stripe_price_id': 'price_pro_999',  # Set this from Stripe Dashboard
        'tier': 'pro',
        'addons': ['advanced-models']
    },
    'enterprise': {
        'name': 'Tri-Agent System',
        'price_usd': 39.99,
        'stripe_price_id': 'price_enterprise_3999',  # Set this from Stripe Dashboard
        'tier': 'enterprise',
        'addons': ['tri-agent-system', 'advanced-models', 'enterprise-features']
    }
}


class UnifiedPayments:
    """
    Unified payment system supporting multiple payment methods.

    Payment Methods:
    - Stripe: Credit/debit cards (wider audience)
    - BTCPay: Bitcoin/Lightning (privacy-focused, zero fees)

    Customer chooses their preferred method.
    """

    def __init__(self):
        self.stripe_available = bool(stripe.api_key)
        self.btcpay_available = bool(BTCPAY_API_KEY)

        if not (self.stripe_available or self.btcpay_available):
            raise ValueError("At least one payment method must be configured")

        # Initialize BTCPay if available
        if self.btcpay_available:
            try:
                from btcpay import BTCPayClient
                self.btcpay = BTCPayClient(
                    host=BTCPAY_HOST,
                    pem=BTCPAY_API_KEY
                )
            except ImportError:
                print("⚠️  BTCPay library not installed. Run: pip install btcpay")
                self.btcpay_available = False

    def get_available_payment_methods(self) -> Dict:
        """
        Return available payment methods for customer choice.
        """
        methods = {}

        if self.stripe_available:
            methods['stripe'] = {
                'name': 'Credit/Debit Card',
                'provider': 'Stripe',
                'fees': '2.9% + $0.30',
                'processing_time': 'Instant',
                'currencies': ['USD', 'EUR', 'GBP', 'etc'],
                'description': 'Pay with any credit or debit card'
            }

        if self.btcpay_available:
            methods['btcpay'] = {
                'name': 'Bitcoin/Lightning',
                'provider': 'BTCPay Server (Self-Hosted)',
                'fees': 'None (you pay blockchain fee)',
                'processing_time': 'Lightning: Instant, Bitcoin: 10-60 min',
                'currencies': ['BTC'],
                'description': 'Privacy-focused, open source payment'
            }

        return methods

    def create_payment(
        self,
        product_key: str,
        payment_method: Literal['stripe', 'btcpay'],
        customer_email: str,
        success_url: str = "https://github.com/woodman33/tri-agent-system",
        cancel_url: str = "https://github.com/woodman33/tri-agent-system"
    ) -> Dict:
        """
        Create payment for customer's chosen method.

        Args:
            product_key: 'pro' or 'enterprise'
            payment_method: 'stripe' or 'btcpay'
            customer_email: Customer email
            success_url: Redirect after success
            cancel_url: Redirect on cancel

        Returns:
            {
                'payment_id': str,
                'checkout_url': str,
                'payment_method': str,
                'amount_usd': float,
                'additional_info': dict  # Method-specific details
            }
        """
        if product_key not in PRODUCTS:
            raise ValueError(f"Unknown product: {product_key}")

        product = PRODUCTS[product_key]

        if payment_method == 'stripe' and self.stripe_available:
            return self._create_stripe_payment(
                product_key, product, customer_email, success_url, cancel_url
            )

        elif payment_method == 'btcpay' and self.btcpay_available:
            return self._create_btcpay_payment(
                product_key, product, customer_email, success_url
            )

        else:
            raise ValueError(f"Payment method '{payment_method}' not available")

    def _create_stripe_payment(
        self,
        product_key: str,
        product: Dict,
        customer_email: str,
        success_url: str,
        cancel_url: str
    ) -> Dict:
        """Create Stripe checkout session."""
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': product['stripe_price_id'],
                'quantity': 1,
            }],
            mode='payment',  # One-time payment
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata={
                'product_key': product_key,
                'tier': product['tier'],
                'payment_method': 'stripe'
            }
        )

        return {
            'payment_id': session.id,
            'checkout_url': session.url,
            'payment_method': 'stripe',
            'amount_usd': product['price_usd'],
            'additional_info': {
                'stripe_session_id': session.id,
                'fees': '2.9% + $0.30',
                'processing': 'Instant'
            }
        }

    def _create_btcpay_payment(
        self,
        product_key: str,
        product: Dict,
        customer_email: str,
        success_url: str
    ) -> Dict:
        """Create BTCPay invoice."""
        order_id = f"{product_key}-{secrets.token_hex(8)}"

        invoice = self.btcpay.create_invoice({
            'price': product['price_usd'],
            'currency': 'USD',
            'orderId': order_id,
            'itemDesc': product['name'],
            'notificationEmail': customer_email,
            'redirectURL': success_url,
            'buyer': {'email': customer_email},
            'metadata': {
                'product_key': product_key,
                'tier': product['tier'],
                'payment_method': 'btcpay'
            }
        })

        return {
            'payment_id': invoice['id'],
            'checkout_url': invoice['url'],
            'payment_method': 'btcpay',
            'amount_usd': product['price_usd'],
            'additional_info': {
                'btc_amount': invoice['btcPrice'],
                'lightning_invoice': invoice.get('lightningInvoice', ''),
                'fees': 'None (blockchain only)',
                'processing': 'Lightning: Instant, Bitcoin: 10-60 min'
            }
        }

    def handle_webhook(
        self,
        payment_method: Literal['stripe', 'btcpay'],
        payload: bytes,
        signature: Optional[str] = None
    ) -> Dict:
        """
        Handle webhook from either payment provider.

        Args:
            payment_method: 'stripe' or 'btcpay'
            payload: Raw webhook payload
            signature: Webhook signature (Stripe only)

        Returns:
            {
                'event_type': str,
                'license_key': str (if payment confirmed),
                'customer_email': str,
                'tier': str,
                'payment_method': str
            }
        """
        if payment_method == 'stripe':
            return self._handle_stripe_webhook(payload, signature)
        elif payment_method == 'btcpay':
            return self._handle_btcpay_webhook(payload)
        else:
            raise ValueError(f"Unknown payment method: {payment_method}")

    def _handle_stripe_webhook(self, payload: bytes, signature: str) -> Dict:
        """Handle Stripe webhook with signature verification."""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid signature")

        if event.type == 'checkout.session.completed':
            session = event.data.object
            customer_email = session.customer_email or session.customer_details.email
            product_key = session.metadata.get('product_key')
            tier = session.metadata.get('tier')

            # Generate license
            license_key = self._generate_license_key()

            # Save license
            self._save_license(
                license_key=license_key,
                email=customer_email,
                tier=tier,
                product_key=product_key,
                payment_method='stripe',
                payment_id=session.id,
                stripe_customer_id=session.customer
            )

            # Send email
            self._send_license_email(customer_email, license_key, tier, 'stripe')

            return {
                'event_type': 'payment_confirmed',
                'license_key': license_key,
                'customer_email': customer_email,
                'tier': tier,
                'payment_method': 'stripe'
            }

        return {'event_type': event.type, 'handled': False}

    def _handle_btcpay_webhook(self, payload: Dict) -> Dict:
        """Handle BTCPay webhook."""
        event_type = payload.get('type')
        invoice_data = payload.get('data', {})

        if event_type == 'InvoicePaymentSettled':
            metadata = invoice_data.get('metadata', {})
            customer_email = metadata.get('customer_email')
            product_key = metadata.get('product_key')
            tier = metadata.get('tier')

            # Generate license
            license_key = self._generate_license_key()

            # Save license
            self._save_license(
                license_key=license_key,
                email=customer_email,
                tier=tier,
                product_key=product_key,
                payment_method='btcpay',
                payment_id=invoice_data['id']
            )

            # Send email
            self._send_license_email(customer_email, license_key, tier, 'btcpay')

            return {
                'event_type': 'payment_confirmed',
                'license_key': license_key,
                'customer_email': customer_email,
                'tier': tier,
                'payment_method': 'btcpay'
            }

        return {'event_type': event_type, 'handled': False}

    def _generate_license_key(self) -> str:
        """Generate unique license key: XXXX-XXXX-XXXX-XXXX"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        parts = [
            ''.join(secrets.choice(chars) for _ in range(4))
            for _ in range(4)
        ]
        return '-'.join(parts)

    def _save_license(self, **kwargs):
        """
        Save license to LOCAL database (JSON file).
        Stored ONLY on your machine, not on payment providers.
        """
        license_db = Path.home() / '.doubledown-studios' / 'licenses.json'
        license_db.parent.mkdir(exist_ok=True)

        # Load existing licenses
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
            'valid': True
        }

        # Save
        with open(license_db, 'w') as f:
            json.dump(licenses, f, indent=2)

        print(f"✅ License saved: {license_key} (paid via {kwargs['payment_method']})")

    def _send_license_email(
        self,
        email: str,
        license_key: str,
        tier: str,
        payment_method: str
    ):
        """
        Send license key via email.

        For production, integrate with:
        - Your own SMTP server
        - Self-hosted Mailgun
        - Postfix on your VPS
        """
        payment_emoji = '💳' if payment_method == 'stripe' else '₿'

        print(f"📧 Email to {email}:")
        print(f"   Payment Method: {payment_emoji} {payment_method.upper()}")
        print(f"   License Key: {license_key}")
        print(f"   Tier: {tier}")
        print(f"   Activation: ./activate.sh")

        # TODO: Implement actual email sending
        # smtp_server = os.getenv('SMTP_SERVER')
        # smtp_user = os.getenv('SMTP_USER')
        # smtp_password = os.getenv('SMTP_PASSWORD')


# FastAPI integration
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse

app = FastAPI(title="Double Down Studios - Unified Payments")

payments = UnifiedPayments()


@app.get("/payment-methods")
async def get_payment_methods():
    """
    Show available payment methods to customer.

    Returns:
        {
            'stripe': {...},
            'btcpay': {...}
        }

    Customer chooses their preferred method.
    """
    return payments.get_available_payment_methods()


@app.post("/create-payment/{product}")
async def create_payment(
    product: str,
    payment_method: str = Query(..., description="'stripe' or 'btcpay'"),
    email: str = Query(..., description="Customer email")
):
    """
    Create payment with customer's chosen method.

    Usage:
        POST /create-payment/enterprise?payment_method=stripe&email=user@example.com
        POST /create-payment/enterprise?payment_method=btcpay&email=user@example.com

    Returns payment details and checkout URL.
    """
    try:
        result = payments.create_payment(
            product_key=product,
            payment_method=payment_method,
            customer_email=email,
            success_url="https://github.com/woodman33/tri-agent-system",
            cancel_url="https://github.com/woodman33/tri-agent-system"
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """
    Stripe webhook endpoint.

    Configure in Stripe Dashboard:
        URL: https://your-api.com/webhooks/stripe
        Events: checkout.session.completed
    """
    payload = await request.body()
    signature = request.headers.get('stripe-signature')

    try:
        result = payments.handle_webhook('stripe', payload, signature)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/webhooks/btcpay")
async def btcpay_webhook(request: Request):
    """
    BTCPay webhook endpoint.

    Configure in BTCPay Dashboard:
        URL: https://your-api.com/webhooks/btcpay
        Events: InvoicePaymentSettled
    """
    payload = await request.json()

    try:
        result = payments.handle_webhook('btcpay', payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check with payment method status"""
    return {
        'status': 'healthy',
        'stripe_available': payments.stripe_available,
        'btcpay_available': payments.btcpay_available
    }


# Example usage
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Double Down Studios - Unified Payment System")
    print("=" * 60)
    print()

    # Show available payment methods
    methods = payments.get_available_payment_methods()
    print("Available Payment Methods:")
    for key, info in methods.items():
        print(f"\n  {info['name']} ({info['provider']})")
        print(f"    Fees: {info['fees']}")
        print(f"    Processing: {info['processing_time']}")

    print()
    print("Starting server...")
    print("  GET  /payment-methods - Show available options")
    print("  POST /create-payment/{product} - Create payment")
    print("  POST /webhooks/stripe - Stripe webhook")
    print("  POST /webhooks/btcpay - BTCPay webhook")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8004)
