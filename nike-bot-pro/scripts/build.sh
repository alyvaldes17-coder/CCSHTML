#!/bin/bash
# Build script for Nike Bot Commercial

echo "🔨 Building Nike Bot Commercial"
echo "================================"

# Build frontend
echo "Building iOS app..."
cd app
npm run tauri build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "📦 Output location:"
    echo "  Windows: app/src-tauri/target/release/nike-bot-commercial.exe"
    echo "  macOS:   app/src-tauri/target/release/bundle/macos/nike-bot-commercial.app"
    echo "  Linux:   app/src-tauri/target/release/bundle/appimage/nike-bot-commercial.AppImage"
else
    echo "✗ Build failed"
    exit 1
fi
