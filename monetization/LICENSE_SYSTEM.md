# GitHub-First Monetization Strategy

## 🎯 Overview

**Everything on GitHub, purchases trigger addons**

Users download from GitHub → Try free features → Purchase unlocks premium addons

## 📦 Distribution Model

### Repository Structure

```
github.com/yourname/local-ai-studio
├── README.md
├── LICENSE (MIT for free tier)
├── src/
│   ├── frontend/
│   ├── backend/
│   └── core/
├── addons/                    (Premium features)
│   ├── tri-agent-system/      (Encrypted/locked)
│   ├── advanced-models/       (Encrypted/locked)
│   └── enterprise-features/   (Encrypted/locked)
├── scripts/
│   ├── install.sh
│   ├── activate-addon.sh
│   └── check-license.sh
└── .github/
    └── workflows/
```

## 💰 Pricing Tiers

### Free (GitHub Download)
- ✅ 2 models (Qwen 2.5 3B, Llama 3.2 8B)
- ✅ Basic chat interface
- ✅ Local inference
- ✅ Full source code (MIT)

### Pro Tier ($9.99 one-time via Gumroad/LemonSqueezy)
- ✅ All 4 models
- ✅ Enhanced UI
- ✅ Priority model loading
- ✅ Custom themes

### Enterprise Tier ($39.99 one-time)
- ✅ Everything in Pro
- ✅ **Tri-Agent System addon**
- ✅ Advanced monitoring
- ✅ Team collaboration features
- ✅ Priority support

## 🔐 License Activation Flow

### User Journey

```
1. Clone from GitHub
   git clone https://github.com/yourname/local-ai-studio

2. Install free version
   ./install.sh

3. Use free features
   [Shows "Upgrade to Pro" prompts]

4. Click "Upgrade" button
   → Opens browser to payment page (Gumroad)

5. Complete purchase
   → Receives license key via email

6. Enter license key in app
   → Addon automatically downloads & activates

7. Features unlock immediately
   → No restart needed
```

## 🛠️ Technical Implementation

### 1. License File Format

```json
{
  "license_key": "XXXX-XXXX-XXXX-XXXX",
  "email": "user@example.com",
  "tier": "enterprise",
  "activated_at": "2025-11-09T00:00:00Z",
  "machine_id": "abc123...",
  "addons": [
    "tri-agent-system",
    "advanced-models"
  ],
  "valid": true
}
```

Stored at: `~/.local-ai-studio/license.json`

### 2. Purchase Flow Integration

**In-App Purchase Button:**
```html
<!-- frontend/src/components/UpgradePrompt.jsx -->
<div className="upgrade-banner">
  <h3>🚀 Unlock Autonomous Agents</h3>
  <p>Tri-Agent System: 6 agents working together</p>
  <button onClick={openPurchasePage}>
    Upgrade to Enterprise - $39.99
  </button>
</div>
```

**Opens Payment Page:**
```javascript
function openPurchasePage() {
  // Opens browser to Gumroad/LemonSqueezy
  const purchaseUrl = 'https://yourname.gumroad.com/l/local-ai-studio-enterprise';

  // Pre-fill with machine ID for hardware locking
  const machineId = getMachineId();
  const fullUrl = `${purchaseUrl}?machine_id=${machineId}`;

  shell.openExternal(fullUrl);
}
```

### 3. Activation System

```python
# backend/license/activator.py

import hashlib
import json
import requests
from pathlib import Path

LICENSE_FILE = Path.home() / '.local-ai-studio' / 'license.json'
VALIDATION_URL = 'https://api.yoursite.com/validate'

def activate_license(license_key: str, email: str):
    """
    Activate license with remote validation.

    Flow:
    1. User enters key
    2. Validate with server
    3. Download addons
    4. Save license locally
    5. Unlock features
    """

    # Get machine ID for hardware lock
    machine_id = get_machine_id()

    # Validate with server
    response = requests.post(VALIDATION_URL, json={
        'license_key': license_key,
        'email': email,
        'machine_id': machine_id
    })

    if response.status_code != 200:
        return False, "Invalid license key"

    data = response.json()

    if not data['valid']:
        return False, data.get('error', 'License validation failed')

    # Download addons
    tier = data['tier']
    addons = data['addons']

    for addon in addons:
        download_addon(addon, data['download_url'])

    # Save license locally
    license_data = {
        'license_key': license_key,
        'email': email,
        'tier': tier,
        'machine_id': machine_id,
        'addons': addons,
        'valid': True,
        'activated_at': data['activated_at']
    }

    LICENSE_FILE.parent.mkdir(exist_ok=True)
    with open(LICENSE_FILE, 'w') as f:
        json.dump(license_data, f, indent=2)

    return True, f"License activated! {len(addons)} addons unlocked."

def get_machine_id():
    """Generate unique machine ID"""
    import platform
    import uuid

    # Combine hostname + MAC address
    hostname = platform.node()
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff)
                    for i in range(0,8*6,8)][::-1])

    unique_str = f"{hostname}-{mac}"
    return hashlib.sha256(unique_str.encode()).hexdigest()[:16]

def download_addon(addon_name: str, base_url: str):
    """Download and extract addon"""
    addon_url = f"{base_url}/{addon_name}.tar.gz"
    addon_dir = Path.home() / '.local-ai-studio' / 'addons' / addon_name

    print(f"Downloading {addon_name}...")

    response = requests.get(addon_url, stream=True)

    if response.status_code != 200:
        print(f"Failed to download {addon_name}")
        return False

    # Save and extract
    import tarfile
    import io

    tar = tarfile.open(fileobj=io.BytesIO(response.content))
    addon_dir.parent.mkdir(parents=True, exist_ok=True)
    tar.extractall(addon_dir)

    print(f"✅ {addon_name} installed")
    return True

def check_license():
    """Check if valid license exists"""
    if not LICENSE_FILE.exists():
        return False, None

    with open(LICENSE_FILE) as f:
        license_data = json.load(f)

    # Basic validation
    if not license_data.get('valid'):
        return False, None

    # Check machine ID matches
    if license_data.get('machine_id') != get_machine_id():
        return False, None

    return True, license_data
```

### 4. Feature Gating

```python
# backend/features/gates.py

def requires_tier(tier_name: str):
    """Decorator to gate features by tier"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            is_licensed, license_data = check_license()

            if not is_licensed:
                return {
                    'error': 'License required',
                    'upgrade_url': 'https://yourname.gumroad.com/l/local-ai-studio'
                }

            user_tier = license_data.get('tier', 'free')
            tier_hierarchy = ['free', 'pro', 'enterprise']

            if tier_hierarchy.index(user_tier) < tier_hierarchy.index(tier_name):
                return {
                    'error': f'{tier_name.title()} tier required',
                    'current_tier': user_tier,
                    'upgrade_url': 'https://yourname.gumroad.com/l/local-ai-studio'
                }

            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage in API endpoints
@app.post('/api/agents/spawn')
@requires_tier('enterprise')
def spawn_agents(request):
    """Spawn tri-agent team (Enterprise only)"""
    # Implementation...
    pass
```

## 🎨 UI Purchase Prompts

### Subtle Banner (Free Users)
```jsx
// frontend/src/components/UpgradeBanner.jsx

export function UpgradeBanner() {
  return (
    <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-lg mb-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-bold">🚀 Unlock Autonomous Agents</h3>
          <p className="text-sm">6-agent system with Boyle's Law spawning</p>
        </div>
        <button
          onClick={openPurchase}
          className="bg-white text-blue-600 px-6 py-2 rounded-lg font-bold hover:bg-gray-100"
        >
          Upgrade - $39.99
        </button>
      </div>
    </div>
  )
}
```

### Feature-Specific Prompts
```jsx
// When user tries to use locked feature

export function FeatureLockedModal({ feature }) {
  return (
    <div className="modal">
      <div className="modal-content">
        <h2>🔒 {feature} is a Premium Feature</h2>

        <div className="feature-preview">
          <img src={`/images/${feature}-preview.png`} />
          <p>This feature is available in Enterprise tier</p>
        </div>

        <div className="pricing">
          <div className="tier">
            <h3>Pro</h3>
            <p>$9.99 one-time</p>
            <ul>
              <li>✅ 4 models</li>
              <li>✅ Enhanced UI</li>
            </ul>
            <button onClick={() => purchase('pro')}>
              Buy Pro
            </button>
          </div>

          <div className="tier featured">
            <span className="badge">BEST VALUE</span>
            <h3>Enterprise</h3>
            <p>$39.99 one-time</p>
            <ul>
              <li>✅ Everything in Pro</li>
              <li>✅ Tri-Agent System</li>
              <li>✅ Advanced features</li>
            </ul>
            <button onClick={() => purchase('enterprise')}>
              Buy Enterprise
            </button>
          </div>
        </div>

        <button onClick={close}>Maybe Later</button>
      </div>
    </div>
  )
}
```

### GitHub README Badges
```markdown
# Local AI Studio

[![GitHub stars](https://img.shields.io/github/stars/yourname/local-ai-studio)](https://github.com/yourname/local-ai-studio)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Buy Pro](https://img.shields.io/badge/Buy-Pro%20$9.99-blue)](https://yourname.gumroad.com/l/local-ai-studio-pro)
[![Buy Enterprise](https://img.shields.io/badge/Buy-Enterprise%20$39.99-purple)](https://yourname.gumroad.com/l/local-ai-studio-enterprise)

## Features

### Free Tier ✅
- 2 open-source models
- Local inference
- Basic chat interface

### Pro Tier 💎 ($9.99)
- All 4 models
- Enhanced UI
- [Buy Now](https://yourname.gumroad.com/l/local-ai-studio-pro)

### Enterprise Tier 🚀 ($39.99)
- **Tri-Agent System** - 6 autonomous agents
- Advanced monitoring
- [Buy Now](https://yourname.gumroad.com/l/local-ai-studio-enterprise)
```

## 💳 Payment Providers

### Option 1: Gumroad (Easiest)
**Pros:**
- ✅ Simple setup
- ✅ Handles payments, VAT, refunds
- ✅ Email delivery
- ✅ 10% fee

**Setup:**
```bash
# 1. Create product on Gumroad
# 2. Set price: $39.99
# 3. Set "License Keys" to generate keys
# 4. Add webhook for activation API
```

### Option 2: LemonSqueezy
**Pros:**
- ✅ Developer-friendly
- ✅ Good API
- ✅ Lower fees (5%)
- ✅ EU VAT compliant

### Option 3: Paddle
**Pros:**
- ✅ Merchant of record (handles taxes)
- ✅ Professional
- ✅ Higher fees (5% + $0.50)

## 🔄 Addon Auto-Update

```python
# backend/addons/updater.py

def check_addon_updates():
    """Check if addons have updates"""
    is_licensed, license_data = check_license()

    if not is_licensed:
        return

    addons = license_data.get('addons', [])

    for addon in addons:
        latest_version = get_latest_version(addon)
        current_version = get_installed_version(addon)

        if latest_version > current_version:
            print(f"Update available for {addon}: {current_version} → {latest_version}")
            download_addon_update(addon, latest_version)
```

## 📊 Analytics & Conversion

```python
# Track upgrade funnel

events = [
    'app_opened',
    'upgrade_banner_shown',
    'upgrade_button_clicked',
    'purchase_page_opened',
    'license_activated'
]

# Simple analytics (no tracking libs needed)
def track_event(event_name, properties=None):
    """Anonymous usage tracking"""
    data = {
        'event': event_name,
        'timestamp': datetime.now().isoformat(),
        'properties': properties or {}
    }

    # Send to your server (optional)
    requests.post('https://api.yoursite.com/track', json=data)
```

## 🎯 Conversion Optimization

### In-App Prompts (Non-Intrusive)
1. **On first launch**: "Welcome! Try Pro free for 7 days"
2. **After 10 chats**: "Enjoying Local AI Studio? Upgrade for more models"
3. **When trying locked feature**: Show feature preview + upgrade options
4. **After successful task**: "Want to automate this? Try our agent system"

### GitHub README
- Clear feature comparison table
- Video demos of Pro/Enterprise features
- Customer testimonials
- "Buy" badges prominent

### Social Proof
```markdown
## Trusted by 10,000+ Users

⭐⭐⭐⭐⭐ "Best local AI solution I've used" - @developer1
⭐⭐⭐⭐⭐ "The agent system is incredible" - @user2
```

Want me to build the complete activation system with UI components next?
