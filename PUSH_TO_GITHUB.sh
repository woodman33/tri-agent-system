#!/bin/bash
#
# Push Tri-Agent System to GitHub
# Run this after creating the repository on GitHub.com
#

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  Pushing Tri-Agent System to GitHub"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if we're in the right directory
if [ ! -d "monetization" ]; then
    echo "Error: Must run from tri-agent-system directory"
    exit 1
fi

# Create .gitignore if it doesn't exist
cat > .gitignore << 'EOF'
# Environment variables (NEVER COMMIT)
.env
.env.*
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# License database (keep private)
licenses.json
.doubledown-studios/

# Dependencies
node_modules/

# Build outputs
dist/
build/
*.egg-info/
EOF

echo "✓ .gitignore created"
echo ""

# Initialize git if not already
if [ ! -d ".git" ]; then
    git init
    echo "✓ Git initialized"
else
    echo "✓ Git already initialized"
fi

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Tri-Agent System v1.0

Features:
- 3-agent autonomous system (Coder, Improver, Doctor)
- Boyle's Law spawning mechanism
- Dual-layer architecture (primary + shadow)
- 100% local with Ollama/vLLM
- Complete monetization system (Stripe + BTCPay)
- React UI components
- License management
- Deployment automation

Ready for production! 🚀" || echo "Commit already exists"

# Set main branch
git branch -M main

# Add remote (replace with your actual GitHub URL)
GITHUB_URL="https://github.com/woodman33/tri-agent-system.git"

if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "$GITHUB_URL"
    echo "✓ Remote added: $GITHUB_URL"
else
    echo "✓ Remote already exists"
fi

echo ""
echo "Ready to push to GitHub!"
echo ""
echo "Run this command to push:"
echo "  git push -u origin main"
echo ""
echo "Then visit:"
echo "  https://github.com/woodman33/tri-agent-system"
echo ""
