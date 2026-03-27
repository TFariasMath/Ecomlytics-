#!/bin/bash
# Docker Quick Start Script

echo "🐳 Analytics Pipeline - Docker Quick Start"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your credentials before continuing."
    echo ""
    read -p "Press enter to continue after editing .env file..."
fi

echo "🔨 Building Docker image..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
    echo ""
    echo "🚀 Starting containers..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Analytics Pipeline started successfully!"
        echo ""
        echo "📊 Dashboard: http://localhost:8501"
        echo ""
        echo "Useful commands:"
        echo "  - View logs:        docker-compose logs -f"
        echo "  - Stop containers:  docker-compose down"
        echo "  - Restart:          docker-compose restart"
        echo ""
    else
        echo "❌ Failed to start containers"
        exit 1
    fi
else
    echo "❌ Failed to build Docker image"
    exit 1
fi
