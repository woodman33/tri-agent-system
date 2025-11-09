"""
License Validation API Server
Validates license keys and provides addon downloads

Run with: uvicorn api_server:app --reload
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import hashlib
import secrets
from datetime import datetime

app = FastAPI(title="License Validation API")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In production, use a database. For demo, using in-memory dict
LICENSE_DATABASE = {
    # Example license keys (replace with your Gumroad/LemonSqueezy webhook)
    "DEMO-1234-5678-ABCD": {
        "email": "demo@example.com",
        "tier": "pro",
        "addons": ["advanced-models"],
        "created_at": "2025-11-09T00:00:00Z",
        "valid": True
    },
    "ENTP-9999-8888-7777": {
        "email": "enterprise@example.com",
        "tier": "enterprise",
        "addons": ["tri-agent-system", "advanced-models", "enterprise-features"],
        "created_at": "2025-11-09T00:00:00Z",
        "valid": True
    }
}


class LicenseValidationRequest(BaseModel):
    license_key: str
    email: EmailStr
    machine_id: str
    app_version: Optional[str] = "1.0.0"


class LicenseValidationResponse(BaseModel):
    valid: bool
    tier: Optional[str] = None
    addons: Optional[List[str]] = None
    download_token: Optional[str] = None
    activated_at: Optional[str] = None
    error: Optional[str] = None


@app.post("/validate", response_model=LicenseValidationResponse)
async def validate_license(request: LicenseValidationRequest):
    """
    Validate a license key.

    Called when user activates license in the app.
    """
    license_key = request.license_key.strip().upper()

    # Check if key exists
    if license_key not in LICENSE_DATABASE:
        return LicenseValidationResponse(
            valid=False,
            error="Invalid license key"
        )

    license_info = LICENSE_DATABASE[license_key]

    # Check if key is valid
    if not license_info.get('valid', False):
        return LicenseValidationResponse(
            valid=False,
            error="License has been revoked"
        )

    # Check email matches
    if license_info['email'].lower() != request.email.lower():
        return LicenseValidationResponse(
            valid=False,
            error="Email does not match license key"
        )

    # Generate secure download token
    download_token = secrets.token_urlsafe(32)

    # Store machine ID (for hardware locking - optional)
    license_info['machine_id'] = request.machine_id
    license_info['last_activated'] = datetime.now().isoformat()

    return LicenseValidationResponse(
        valid=True,
        tier=license_info['tier'],
        addons=license_info.get('addons', []),
        download_token=download_token,
        activated_at=license_info.get('created_at')
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "license-validation-api"}


@app.post("/webhooks/gumroad")
async def gumroad_webhook(
    payload: dict,
    x_gumroad_signature: Optional[str] = Header(None)
):
    """
    Webhook from Gumroad on purchase.

    Automatically creates license key on purchase.
    """
    # Verify signature (production)
    # verify_gumroad_signature(payload, x_gumroad_signature)

    # Extract purchase info
    sale_id = payload.get('sale_id')
    email = payload.get('email')
    product_id = payload.get('product_id')
    license_key = payload.get('license_key')  # Gumroad generates this

    # Determine tier based on product
    tier_map = {
        'pro_product_id': 'pro',
        'enterprise_product_id': 'enterprise'
    }

    tier = tier_map.get(product_id, 'pro')

    # Add to database
    LICENSE_DATABASE[license_key] = {
        "email": email,
        "tier": tier,
        "addons": get_addons_for_tier(tier),
        "created_at": datetime.now().isoformat(),
        "valid": True,
        "sale_id": sale_id
    }

    print(f"✅ New license created: {license_key} ({tier})")

    return {"status": "success"}


def get_addons_for_tier(tier: str) -> List[str]:
    """Get addons for a given tier"""
    addon_map = {
        'pro': ['advanced-models'],
        'enterprise': ['tri-agent-system', 'advanced-models', 'enterprise-features']
    }

    return addon_map.get(tier, [])


@app.get("/addons/{addon_name}")
async def get_addon_info(addon_name: str):
    """Get addon information"""
    addons = {
        'tri-agent-system': {
            'name': 'Tri-Agent System',
            'description': '6-agent autonomous system with Boyle\'s Law spawning',
            'version': '1.0.0',
            'size': '15MB',
            'required_tier': 'enterprise'
        },
        'advanced-models': {
            'name': 'Advanced Models Pack',
            'description': 'Additional 2 premium models',
            'version': '1.0.0',
            'size': '8GB',
            'required_tier': 'pro'
        }
    }

    if addon_name not in addons:
        raise HTTPException(status_code=404, detail="Addon not found")

    return addons[addon_name]


# Run with: uvicorn api_server:app --reload --port 8001
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
