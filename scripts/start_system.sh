#!/bin/bash

# Trading System - Start Script
# Startet das komplette Trading-System

set -e

echo "🚀 Starting Trading System..."
echo "================================"

# Überprüfe ob .env existiert
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Überprüfe Docker
if command -v docker-compose &> /dev/null; then
    echo "🐳 Starting with Docker Compose..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    echo "🔍 Checking service health..."
    docker-compose ps
    
    echo ""
    echo "✅ Trading System started successfully!"
    echo ""
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔗 API: http://localhost:5001/api/health"
    echo ""
    echo "📋 Useful commands:"
    echo "  docker-compose logs -f trading-api    # View API logs"
    echo "  docker-compose logs -f trading-dashboard  # View dashboard logs"
    echo "  docker-compose down                   # Stop system"
    echo ""
    
elif command -v python3 &> /dev/null; then
    echo "🐍 Starting with Python (local mode)..."
    
    # Backend starten
    echo "Starting backend..."
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    nohup python main_simple.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    cd ..
    
    # Frontend starten
    if command -v npm &> /dev/null; then
        echo "Starting frontend..."
        cd frontend
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        nohup npm run dev > ../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo "Frontend started with PID: $FRONTEND_PID"
        cd ..
        
        echo ""
        echo "✅ Trading System started successfully!"
        echo ""
        echo "📊 Dashboard: http://localhost:5174"
        echo "🔗 API: http://localhost:5001/api/health"
        echo ""
        echo "📋 Process IDs:"
        echo "  Backend PID: $BACKEND_PID"
        echo "  Frontend PID: $FRONTEND_PID"
        echo ""
        echo "To stop the system:"
        echo "  kill $BACKEND_PID $FRONTEND_PID"
        echo ""
    else
        echo "❌ npm not found. Please install Node.js"
        kill $BACKEND_PID
        exit 1
    fi
    
else
    echo "❌ Neither Docker nor Python found!"
    echo "Please install Docker or Python 3.11+"
    exit 1
fi

echo "🎉 System is ready for trading!"

