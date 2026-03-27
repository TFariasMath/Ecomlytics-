#!/bin/bash
# ==============================================
# Quick Deploy Script for VPS
# Run this on the VPS after uploading the project
# ==============================================

set -e

echo "======================================"
echo "🚀 Analytics Dashboard - Quick Deploy"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed. Installing..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please logout and login again, then re-run this script."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "📝 Please edit .env with your credentials:"
        echo "   nano .env"
        exit 1
    else
        echo "❌ .env.example not found. Create .env manually."
        exit 1
    fi
fi

echo ""
echo "📦 Building Docker image..."
docker compose build

echo ""
echo "🚀 Starting containers..."
docker compose up -d

echo ""
echo "⏳ Waiting for startup..."
sleep 10

echo ""
echo "🔍 Checking status..."
docker compose ps

echo ""
echo "======================================"
echo "✅ Deploy Complete!"
echo "======================================"
echo ""
echo "🌐 Access your dashboard at:"
echo "   http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "📱 This URL works on PC, phone, and tablet!"
echo ""
echo "📋 Useful commands:"
echo "   docker compose logs -f     # View logs"
echo "   docker compose restart     # Restart"
echo "   docker compose down        # Stop"
echo ""
