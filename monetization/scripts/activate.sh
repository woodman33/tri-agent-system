#!/bin/bash
#
# Tri-Agent System Activation Script
# Double Down Studios
#
# Activates license and downloads addons

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  Tri-Agent System - License Activation"
echo "  By Double Down Studios"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Local AI Studio is installed
echo "Checking dependencies..."

if [ ! -d "$HOME/local-ai-studio" ]; then
    echo -e "${RED}✗ Local AI Studio not found${NC}"
    echo ""
    echo "Tri-Agent System requires Local AI Studio to be installed first."
    echo ""
    echo "Install Local AI Studio:"
    echo "  git clone https://github.com/woodman33/local-ai-studio.git ~/local-ai-studio"
    echo "  cd ~/local-ai-studio"
    echo "  ./install.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Local AI Studio found${NC}"

# Check if vLLM is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠  vLLM server not running${NC}"
    echo ""
    echo "Please start Local AI Studio first:"
    echo "  cd ~/local-ai-studio"
    echo "  ./start.sh"
    echo ""
    read -p "Press Enter when Local AI Studio is running..."
fi

echo -e "${GREEN}✓ vLLM server detected${NC}"
echo ""

# Get license info
echo "Enter your license details:"
echo "(You received these via email after purchase)"
echo ""

read -p "License Key: " LICENSE_KEY
read -p "Email: " EMAIL

# Clean license key
LICENSE_KEY=$(echo "$LICENSE_KEY" | tr '[:lower:]' '[:upper:]' | tr -d ' ')

echo ""
echo "Validating license..."

# Call Python license manager
python3 << END
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.license_manager import LicenseManager

manager = LicenseManager('tri-agent-system')

success, message = manager.activate_license(
    license_key='$LICENSE_KEY',
    email='$EMAIL',
    validate_online=True
)

if success:
    print('\n${GREEN}✓ License activated successfully!${NC}')
    print(message)
    sys.exit(0)
else:
    print('\n${RED}✗ Activation failed${NC}')
    print(message)
    sys.exit(1)
END

ACTIVATION_RESULT=$?

if [ $ACTIVATION_RESULT -eq 0 ]; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Tri-Agent System Activated! 🎉${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Your 6-agent autonomous system is ready!"
    echo ""
    echo "Quick Start:"
    echo "  cd ~/tri-agent-system"
    echo "  ./run-demo.sh"
    echo ""
    echo "Or integrate with Local AI Studio and use via the UI."
    echo ""
    echo "Documentation: https://github.com/woodman33/tri-agent-system/docs"
    echo ""
else
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  Activation Failed${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Please check:"
    echo "  • License key is correct"
    echo "  • Email matches purchase email"
    echo "  • Internet connection is active"
    echo ""
    echo "Need help? Contact support@doubledownstudios.com"
    echo ""
    exit 1
fi
