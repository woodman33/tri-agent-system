"""
Stripe Integration for Double Down Studios
Handles payments, subscriptions, and license generation

Setup:
    pip install stripe
    export STRIPE_SECRET_KEY=sk_test_...
    export STRIPE_WEBHOOK_SECRET=whsec_...
"""
import stripe
import os
import secrets
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
from pathlib import Path

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Webhook secret for signature verification
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Your product IDs (create these in Stripe Dashboard)
PRODUCTS = {
    'pro': {
        'price_id': 'price_pro_999',  # $9.99 one-time
        'name': 'Local AI Studio Pro',
        'tier': 'pro',
        'addons': ['advanced-models']
    },
    'enterprise': {
        'price_id': 'price_enterprise_3999',  # $39.99 one-time
        'name': 'Tri-Agent System',
        'tier': 'enterprise',
        'addons': ['tri-agent-system', 'advanced-models', 'enterprise-features']
    }
}


class StripePayments:
    """
    Stripe payment integration for Double Down Studios.

    Features:
    - One-time payments
    - Subscription support (optional)
    - Automatic license generation
    - Webhook handling
    - Customer management
    """

    def __init__(self):
        if not stripe.api_key:
            raise ValueError("STRIPE_SECRET_KEY environment variable not set")

    def create_checkout_session(
        self,
        product_key: str,
        customer_email: Optional[str] = None,
        success_url: str = "https://yoursite.com/success",
        cancel_url: str = "https://yoursite.com/cancel"
    ) -> Dict:
        """
        Create Stripe checkout session for one-time payment.

        Args:
            product_key: 'pro' or 'enterprise'
            customer_email: Pre-fill email
            success_url: Redirect after payment
            cancel_url: Redirect on cancel

        Returns:
            {
                'checkout_url': str,
                'session_id': str
            }
        """
        if product_key not in PRODUCTS:
            raise ValueError(f"Unknown product: {product_key}")

        product = PRODUCTS[product_key]

        # Create checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': product['price_id'],
                'quantity': 1,
            }],
            mode='payment',  # One-time payment
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata={
                'product_key': product_key,
                'tier': product['tier']
            }
        )

        return {
            'checkout_url': session.url,
            'session_id': session.id
        }

    def create_subscription_checkout(
        self,
        product_key: str,
        customer_email: Optional[str] = None,
        success_url: str = "https://yoursite.com/success",
        cancel_url: str = "https://yoursite.com/cancel"
    ) -> Dict:
        """
        Create checkout for recurring subscription (optional).

        For monthly pricing:
            Pro: $4.99/mo
            Enterprise: $14.99/mo
        """
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': PRODUCTS[product_key]['price_id'],
                'quantity': 1,
            }],
            mode='subscription',  # Recurring
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata={
                'product_key': product_key,
                'tier': PRODUCTS[product_key]['tier']
            }
        )

        return {
            'checkout_url': session.url,
            'session_id': session.id
        }

    def handle_webhook(self, payload: bytes, signature: str) -> Dict:
        """
        Handle Stripe webhook events.

        Called when:
        - Payment succeeds
        - Subscription created
        - Payment fails
        - Subscription canceled

        Returns:
            {
                'event_type': str,
                'license_key': str (if applicable),
                'customer_email': str,
                'product': str
            }
        """
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid signature")

        # Handle different event types
        if event.type == 'checkout.session.completed':
            return self._handle_checkout_completed(event.data.object)

        elif event.type == 'payment_intent.succeeded':
            return self._handle_payment_succeeded(event.data.object)

        elif event.type == 'customer.subscription.created':
            return self._handle_subscription_created(event.data.object)

        elif event.type == 'customer.subscription.deleted':
            return self._handle_subscription_canceled(event.data.object)

        return {'event_type': event.type, 'handled': False}

    def _handle_checkout_completed(self, session) -> Dict:
        """
        Handle successful checkout.
        Generate and save license key.
        """
        customer_email = session.customer_email or session.customer_details.email
        product_key = session.metadata.get('product_key')
        tier = session.metadata.get('tier')

        # Generate license key
        license_key = self._generate_license_key()

        # Save to database (replace with your DB)
        self._save_license(
            license_key=license_key,
            email=customer_email,
            tier=tier,
            product_key=product_key,
            stripe_session_id=session.id,
            stripe_customer_id=session.customer
        )

        # Send license email (you'll implement this)
        self._send_license_email(customer_email, license_key, tier)

        return {
            'event_type': 'checkout.completed',
            'license_key': license_key,
            'customer_email': customer_email,
            'tier': tier,
            'product_key': product_key
        }

    def _handle_payment_succeeded(self, payment_intent) -> Dict:
        """Handle successful payment intent"""
        return {
            'event_type': 'payment.succeeded',
            'amount': payment_intent.amount / 100,
            'customer': payment_intent.customer
        }

    def _handle_subscription_created(self, subscription) -> Dict:
        """Handle new subscription"""
        customer_email = stripe.Customer.retrieve(subscription.customer).email

        # Generate license for subscription
        license_key = self._generate_license_key()

        self._save_license(
            license_key=license_key,
            email=customer_email,
            tier='pro',  # Or determine from subscription
            product_key='subscription',
            stripe_subscription_id=subscription.id,
            stripe_customer_id=subscription.customer
        )

        return {
            'event_type': 'subscription.created',
            'license_key': license_key,
            'customer_email': customer_email
        }

    def _handle_subscription_canceled(self, subscription) -> Dict:
        """Handle subscription cancellation"""
        # Deactivate license
        self._deactivate_license_by_subscription(subscription.id)

        return {
            'event_type': 'subscription.canceled',
            'subscription_id': subscription.id
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
        Save license to database.

        In production, use PostgreSQL/MySQL.
        For demo, using JSON file.
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
            'valid': True
        }

        # Save
        with open(license_db, 'w') as f:
            json.dump(licenses, f, indent=2)

        print(f"✅ License saved: {license_key}")

    def _deactivate_license_by_subscription(self, subscription_id: str):
        """Deactivate license when subscription canceled"""
        license_db = Path.home() / '.doubledown-studios' / 'licenses.json'

        if not license_db.exists():
            return

        with open(license_db) as f:
            licenses = json.load(f)

        # Find and deactivate
        for key, data in licenses.items():
            if data.get('stripe_subscription_id') == subscription_id:
                data['valid'] = False
                data['deactivated_at'] = datetime.now().isoformat()
                print(f"🔒 License deactivated: {key}")

        with open(license_db, 'w') as f:
            json.dump(licenses, f, indent=2)

    def _send_license_email(self, email: str, license_key: str, tier: str):
        """
        Send license key via email.

        Integrate with:
        - SendGrid
        - AWS SES
        - Mailgun
        - Postmark
        """
        # TODO: Implement email sending
        print(f"📧 Email to {email}:")
        print(f"   License Key: {license_key}")
        print(f"   Tier: {tier}")
        print(f"   Activation: ./activate.sh")

    def retrieve_session(self, session_id: str) -> Dict:
        """Retrieve checkout session details"""
        session = stripe.checkout.Session.retrieve(session_id)

        return {
            'payment_status': session.payment_status,
            'customer_email': session.customer_email or session.customer_details.email,
            'amount_total': session.amount_total / 100,
            'metadata': session.metadata
        }

    def create_customer_portal_session(
        self,
        customer_id: str,
        return_url: str = "https://yoursite.com/account"
    ) -> str:
        """
        Create customer portal for managing subscription.

        Allows customers to:
        - Update payment method
        - View invoices
        - Cancel subscription
        """
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

        return session.url


# FastAPI integration
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import RedirectResponse

app = FastAPI(title="Double Down Studios - Stripe Integration")

stripe_payments = StripePayments()


@app.post("/create-checkout/{product}")
async def create_checkout(
    product: str,
    email: Optional[str] = None
):
    """
    Create Stripe checkout session.

    Usage:
        POST /create-checkout/pro?email=user@example.com
        POST /create-checkout/enterprise?email=user@example.com

    Returns redirect to Stripe checkout
    """
    try:
        result = stripe_payments.create_checkout_session(
            product_key=product,
            customer_email=email,
            success_url=f"https://yoursite.com/success",
            cancel_url=f"https://yoursite.com/cancel"
        )

        return {
            'checkout_url': result['checkout_url'],
            'session_id': result['session_id']
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """
    Stripe webhook endpoint.

    Configure in Stripe Dashboard:
        URL: https://yourapi.com/webhooks/stripe
        Events: checkout.session.completed, payment_intent.succeeded
    """
    payload = await request.body()
    signature = request.headers.get('stripe-signature')

    try:
        result = stripe_payments.handle_webhook(payload, signature)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/success")
async def payment_success(session_id: str):
    """
    Payment success page.
    Show license key and activation instructions.
    """
    session_data = stripe_payments.retrieve_session(session_id)

    return {
        'success': True,
        'message': 'Payment successful! Check your email for license key.',
        'email': session_data['customer_email'],
        'amount': session_data['amount_total']
    }


# Example usage
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Double Down Studios - Stripe Integration")
    print("=" * 60)
    print()

    # Demo: Create checkout
    payments = StripePayments()

    print("Creating checkout session for Enterprise tier...")
    result = payments.create_checkout_session(
        product_key='enterprise',
        customer_email='demo@example.com'
    )

    print(f"Checkout URL: {result['checkout_url']}")
    print(f"Session ID: {result['session_id']}")
    print()

    # Start server
    print("Starting webhook server...")
    print("Configure Stripe webhook: https://yourapi.com/webhooks/stripe")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8002)
