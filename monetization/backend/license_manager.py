"""
License Manager - Backend
Handles license activation, validation, and addon downloads
"""
import hashlib
import json
import requests
import tarfile
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional, List
import platform
import uuid


class LicenseManager:
    """
    Manages software licenses and addon activations.

    Features:
    - License key validation
    - Hardware locking (optional)
    - Addon downloading and installation
    - Offline validation
    - Tier management
    """

    def __init__(self, app_name: str = "local-ai-studio"):
        self.app_name = app_name
        self.config_dir = Path.home() / f".{app_name}"
        self.config_dir.mkdir(exist_ok=True)

        self.license_file = self.config_dir / "license.json"
        self.addons_dir = self.config_dir / "addons"
        self.addons_dir.mkdir(exist_ok=True)

        # Your validation server (set this up)
        self.validation_url = "https://api.yoursite.com/validate"
        self.download_url = "https://downloads.yoursite.com/addons"

    def get_machine_id(self) -> str:
        """
        Generate unique machine identifier.
        Used for hardware locking (optional).
        """
        hostname = platform.node()
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff)
                        for i in range(0,8*6,8)][::-1])

        unique_str = f"{hostname}-{mac}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]

    def activate_license(
        self,
        license_key: str,
        email: str,
        validate_online: bool = True
    ) -> Tuple[bool, str]:
        """
        Activate a license key.

        Args:
            license_key: License key from purchase
            email: User's email
            validate_online: Validate with server (default True)

        Returns:
            (success, message)
        """
        # Clean license key
        license_key = license_key.strip().upper()

        if validate_online:
            # Online validation
            success, data_or_error = self._validate_online(license_key, email)

            if not success:
                return False, data_or_error

            license_data = data_or_error
        else:
            # Offline validation (basic check)
            if not self._validate_key_format(license_key):
                return False, "Invalid license key format"

            # Create basic license data (no tier info without online validation)
            license_data = {
                'license_key': license_key,
                'email': email,
                'tier': 'unknown',
                'addons': [],
                'validated_offline': True
            }

        # Add machine info
        license_data['machine_id'] = self.get_machine_id()
        license_data['activated_at'] = datetime.now().isoformat()
        license_data['valid'] = True

        # Save license
        self._save_license(license_data)

        # Download addons if online
        if validate_online and 'addons' in license_data:
            for addon in license_data['addons']:
                self._download_addon(addon, license_data.get('download_token'))

        return True, f"License activated! Tier: {license_data['tier']}"

    def _validate_online(self, license_key: str, email: str) -> Tuple[bool, any]:
        """Validate license with remote server"""
        try:
            response = requests.post(
                self.validation_url,
                json={
                    'license_key': license_key,
                    'email': email,
                    'machine_id': self.get_machine_id(),
                    'app_version': '1.0.0'
                },
                timeout=10
            )

            if response.status_code != 200:
                return False, f"Server error: {response.status_code}"

            data = response.json()

            if not data.get('valid'):
                return False, data.get('error', 'License validation failed')

            return True, data

        except requests.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def _validate_key_format(self, key: str) -> bool:
        """Basic offline validation of key format"""
        # Example: XXXX-XXXX-XXXX-XXXX
        parts = key.split('-')

        if len(parts) != 4:
            return False

        for part in parts:
            if len(part) != 4 or not part.isalnum():
                return False

        return True

    def _save_license(self, license_data: Dict):
        """Save license data to disk"""
        with open(self.license_file, 'w') as f:
            json.dump(license_data, f, indent=2)

        print(f"✅ License saved to {self.license_file}")

    def check_license(self) -> Tuple[bool, Optional[Dict]]:
        """
        Check if valid license exists.

        Returns:
            (is_valid, license_data or None)
        """
        if not self.license_file.exists():
            return False, None

        try:
            with open(self.license_file) as f:
                license_data = json.load(f)
        except json.JSONDecodeError:
            return False, None

        # Basic validation
        if not license_data.get('valid'):
            return False, None

        # Check machine ID (if hardware locked)
        if 'machine_id' in license_data:
            if license_data['machine_id'] != self.get_machine_id():
                print("⚠️  License is hardware-locked to different machine")
                return False, None

        return True, license_data

    def get_tier(self) -> str:
        """Get current license tier"""
        is_valid, license_data = self.check_license()

        if not is_valid:
            return 'free'

        return license_data.get('tier', 'free')

    def has_addon(self, addon_name: str) -> bool:
        """Check if addon is available"""
        is_valid, license_data = self.check_license()

        if not is_valid:
            return False

        return addon_name in license_data.get('addons', [])

    def _download_addon(self, addon_name: str, download_token: Optional[str] = None) -> bool:
        """
        Download and install addon.

        Args:
            addon_name: Name of addon (e.g., 'tri-agent-system')
            download_token: Secure download token from server
        """
        addon_dir = self.addons_dir / addon_name

        if addon_dir.exists():
            print(f"ℹ️  {addon_name} already installed")
            return True

        print(f"📦 Downloading {addon_name}...")

        # Construct download URL
        url = f"{self.download_url}/{addon_name}.tar.gz"

        headers = {}
        if download_token:
            headers['Authorization'] = f"Bearer {download_token}"

        try:
            response = requests.get(url, headers=headers, stream=True, timeout=60)

            if response.status_code != 200:
                print(f"❌ Failed to download {addon_name}: {response.status_code}")
                return False

            # Extract tarball
            tar = tarfile.open(fileobj=io.BytesIO(response.content))
            tar.extractall(addon_dir)
            tar.close()

            print(f"✅ {addon_name} installed to {addon_dir}")
            return True

        except Exception as e:
            print(f"❌ Error installing {addon_name}: {str(e)}")
            return False

    def deactivate_license(self) -> bool:
        """Deactivate current license"""
        if self.license_file.exists():
            self.license_file.unlink()
            print("✅ License deactivated")
            return True

        return False

    def get_license_info(self) -> Dict:
        """Get current license information"""
        is_valid, license_data = self.check_license()

        if not is_valid:
            return {
                'tier': 'free',
                'valid': False,
                'addons': []
            }

        return {
            'tier': license_data.get('tier', 'free'),
            'valid': True,
            'email': license_data.get('email'),
            'activated_at': license_data.get('activated_at'),
            'addons': license_data.get('addons', []),
            'machine_id': license_data.get('machine_id')
        }


# Decorator for feature gating
def requires_tier(tier_name: str):
    """
    Decorator to gate features by license tier.

    Usage:
        @requires_tier('pro')
        def advanced_feature():
            # Only accessible to Pro+ users
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = LicenseManager()
            current_tier = manager.get_tier()

            tier_hierarchy = ['free', 'pro', 'enterprise']

            required_level = tier_hierarchy.index(tier_name) if tier_name in tier_hierarchy else 999
            current_level = tier_hierarchy.index(current_tier) if current_tier in tier_hierarchy else 0

            if current_level < required_level:
                return {
                    'error': 'License required',
                    'required_tier': tier_name,
                    'current_tier': current_tier,
                    'upgrade_url': 'https://yourname.gumroad.com/l/local-ai-studio'
                }

            return func(*args, **kwargs)

        return wrapper
    return decorator


def requires_addon(addon_name: str):
    """
    Decorator to gate features by addon.

    Usage:
        @requires_addon('tri-agent-system')
        def spawn_agents():
            # Only if tri-agent addon installed
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = LicenseManager()

            if not manager.has_addon(addon_name):
                return {
                    'error': 'Addon required',
                    'addon': addon_name,
                    'upgrade_url': 'https://yourname.gumroad.com/l/local-ai-studio-enterprise'
                }

            return func(*args, **kwargs)

        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    manager = LicenseManager()

    print("🔐 License Manager Demo\n")

    # Check current license
    print("1. Checking existing license...")
    is_valid, license_data = manager.check_license()

    if is_valid:
        print(f"✅ Licensed: {license_data['tier']}")
        print(f"   Email: {license_data['email']}")
        print(f"   Addons: {', '.join(license_data.get('addons', []))}")
    else:
        print("ℹ️  No license found (Free tier)")

    # Demo activation (offline mode for testing)
    print("\n2. Demo: Activating license (offline mode)...")
    success, message = manager.activate_license(
        license_key="DEMO-1234-5678-ABCD",
        email="demo@example.com",
        validate_online=False  # Skip online validation for demo
    )

    print(f"{'✅' if success else '❌'} {message}")

    # Get info
    print("\n3. License Info:")
    info = manager.get_license_info()
    print(json.dumps(info, indent=2))

    # Demo feature gating
    print("\n4. Demo: Feature gating")

    @requires_tier('enterprise')
    def enterprise_feature():
        return "Enterprise feature executed!"

    result = enterprise_feature()
    print(f"Result: {result}")
