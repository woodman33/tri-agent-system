#!/bin/bash
#
# Production Deployment Script for Double Down Studios
# Deploys unified payment system to self-hosted environment
#

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════"
echo "  Double Down Studios - Production Deployment"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
DEPLOYMENT_TYPE="${1:-local}"  # local, vps, or test

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Check dependencies
echo -e "${BLUE}[1/8]${NC} Checking dependencies..."

if ! command_exists python3; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

if ! command_exists pip; then
    echo -e "${RED}✗ pip not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Step 2: Check environment configuration
echo -e "${BLUE}[2/8]${NC} Checking environment configuration..."

if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${YELLOW}⚠  .env file not found${NC}"
    echo ""
    echo "Creating .env from template..."
    cp "$SCRIPT_DIR/.env.example" "$BACKEND_DIR/.env"
    echo ""
    echo -e "${YELLOW}Please edit $BACKEND_DIR/.env with your actual keys:${NC}"
    echo "  - STRIPE_SECRET_KEY"
    echo "  - STRIPE_WEBHOOK_SECRET"
    echo "  - BTCPAY_HOST"
    echo "  - BTCPAY_API_KEY"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if keys are set
source "$BACKEND_DIR/.env"

if [[ "$STRIPE_SECRET_KEY" == *"YOUR_"* ]] && [[ "$BTCPAY_API_KEY" == *"YOUR_"* ]]; then
    echo -e "${RED}✗ Please configure at least one payment method in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment configured${NC}"
echo ""

# Step 3: Install Python dependencies
echo -e "${BLUE}[3/8]${NC} Installing Python dependencies..."

cd "$BACKEND_DIR"

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
else
    # Create requirements.txt if it doesn't exist
    cat > requirements.txt << 'EOF'
stripe>=7.0.0
btcpay>=1.0.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-dotenv>=1.0.0
python-multipart>=0.0.6
aiofiles>=23.0.0
EOF
    pip install -r requirements.txt -q
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 4: Create necessary directories
echo -e "${BLUE}[4/8]${NC} Creating directories..."

mkdir -p "$HOME/.doubledown-studios"
mkdir -p "$HOME/.doubledown-studios/logs"
mkdir -p "$HOME/.doubledown-studios/backups"

echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Step 5: Test payment system
echo -e "${BLUE}[5/8]${NC} Testing payment system..."

python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, '.')

try:
    from unified_payments import UnifiedPayments

    payments = UnifiedPayments()
    methods = payments.get_available_payment_methods()

    print(f"✓ Payment system initialized")

    if 'stripe' in methods:
        print(f"  ✓ Stripe: Available")
    if 'btcpay' in methods:
        print(f"  ✓ BTCPay: Available")

    if not methods:
        print(f"  ✗ No payment methods configured!")
        sys.exit(1)

except Exception as e:
    print(f"✗ Payment system test failed: {e}")
    sys.exit(1)
PYTHON_TEST

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Payment system test failed${NC}"
    exit 1
fi

echo ""

# Step 6: Start the server based on deployment type
echo -e "${BLUE}[6/8]${NC} Starting server (${DEPLOYMENT_TYPE} mode)..."

case "$DEPLOYMENT_TYPE" in
    local)
        echo "Starting local development server..."
        echo ""
        echo -e "${GREEN}Server will run at: http://localhost:8004${NC}"
        echo ""
        echo "Endpoints:"
        echo "  GET  /payment-methods"
        echo "  POST /create-payment/{product}"
        echo "  POST /webhooks/stripe"
        echo "  POST /webhooks/btcpay"
        echo ""
        echo -e "${YELLOW}Note: For webhooks to work, use ngrok:${NC}"
        echo "  ngrok http 8004"
        echo ""

        uvicorn unified_payments:app --host 127.0.0.1 --port 8004 --reload
        ;;

    test)
        echo "Starting test server with ngrok tunnel..."
        echo ""

        # Check if ngrok is installed
        if ! command_exists ngrok; then
            echo -e "${YELLOW}Installing ngrok...${NC}"
            brew install ngrok
        fi

        # Start server in background
        uvicorn unified_payments:app --host 127.0.0.1 --port 8004 &
        SERVER_PID=$!

        sleep 2

        # Start ngrok tunnel
        echo "Starting ngrok tunnel..."
        ngrok http 8004 &
        NGROK_PID=$!

        echo ""
        echo -e "${GREEN}✓ Server running with public URL${NC}"
        echo ""
        echo "Update your webhooks to use the ngrok URL shown above"
        echo ""
        echo "Press Ctrl+C to stop"

        # Wait for interrupt
        trap "kill $SERVER_PID $NGROK_PID" EXIT
        wait
        ;;

    vps)
        echo "Deploying to VPS..."
        echo ""

        # Create systemd service
        cat > /tmp/doubledown-api.service << EOF
[Unit]
Description=Double Down Studios API
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$PATH"
EnvironmentFile=$BACKEND_DIR/.env
ExecStart=$(which uvicorn) unified_payments:app --host 0.0.0.0 --port 8004
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        echo "Systemd service created at /tmp/doubledown-api.service"
        echo ""
        echo "To install on VPS:"
        echo "  1. sudo cp /tmp/doubledown-api.service /etc/systemd/system/"
        echo "  2. sudo systemctl daemon-reload"
        echo "  3. sudo systemctl enable doubledown-api"
        echo "  4. sudo systemctl start doubledown-api"
        echo ""
        echo "To check status:"
        echo "  sudo systemctl status doubledown-api"
        echo ""
        echo "To view logs:"
        echo "  sudo journalctl -u doubledown-api -f"
        ;;

    *)
        echo -e "${RED}✗ Unknown deployment type: $DEPLOYMENT_TYPE${NC}"
        echo "Usage: ./deploy.sh [local|test|vps]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓ Deployment complete${NC}"
echo ""
