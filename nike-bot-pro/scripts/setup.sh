#!/bin/bash
# Setup script for Nike Bot Commercial

echo "🚀 Nike Bot Commercial - Setup"
echo "================================"

# Check prerequisites
echo "✓ Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Install from python.org"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "✗ Node.js not found. Install from nodejs.org"
    exit 1
fi

if ! command -v rustc &> /dev/null; then
    echo "✗ Rust not found. Install from rustup.rs"
    exit 1
fi

echo "✓ All prerequisites installed"

# Backend setup
echo ""
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✓ Backend setup complete"

# Frontend setup
echo ""
echo "🎨 Setting up frontend..."
cd ../app
npm install
echo "✓ Frontend setup complete"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  Terminal 1 (Backend):  cd backend && source venv/bin/activate && python main.py"
echo "  Terminal 2 (Frontend): cd app && npm run tauri dev"
