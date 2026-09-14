cd "$(dirname "$0")/.."

echo "Making scripts executable..."
chmod +x scripts/setup.sh
chmod +x scripts/start.sh
chmod +x scripts/test.sh
chmod +x scripts/status.sh

echo "✓ All permissions set"
