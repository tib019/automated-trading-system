#!/bin/bash

# Trading System - Stop Script
# Stoppt das komplette Trading-System sicher

set -e

echo "🛑 Stopping Trading System..."
echo "==============================="

# Überprüfe Docker
if command -v docker-compose &> /dev/null && [ -f docker-compose.yml ]; then
    echo "🐳 Stopping Docker containers..."
    docker-compose down
    echo "✅ Docker containers stopped"
else
    echo "🐍 Stopping Python processes..."
    
    # Finde und stoppe Backend-Prozesse
    BACKEND_PIDS=$(pgrep -f "main_simple.py" || true)
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo "Stopping backend processes: $BACKEND_PIDS"
        kill $BACKEND_PIDS
        sleep 2
        
        # Force kill falls nötig
        BACKEND_PIDS=$(pgrep -f "main_simple.py" || true)
        if [ ! -z "$BACKEND_PIDS" ]; then
            echo "Force killing backend processes: $BACKEND_PIDS"
            kill -9 $BACKEND_PIDS
        fi
    fi
    
    # Finde und stoppe Frontend-Prozesse
    FRONTEND_PIDS=$(pgrep -f "npm.*dev\|vite" || true)
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo "Stopping frontend processes: $FRONTEND_PIDS"
        kill $FRONTEND_PIDS
        sleep 2
        
        # Force kill falls nötig
        FRONTEND_PIDS=$(pgrep -f "npm.*dev\|vite" || true)
        if [ ! -z "$FRONTEND_PIDS" ]; then
            echo "Force killing frontend processes: $FRONTEND_PIDS"
            kill -9 $FRONTEND_PIDS
        fi
    fi
    
    # Stoppe alle Flask-Prozesse
    FLASK_PIDS=$(pgrep -f "flask\|werkzeug" || true)
    if [ ! -z "$FLASK_PIDS" ]; then
        echo "Stopping Flask processes: $FLASK_PIDS"
        kill $FLASK_PIDS
    fi
    
    echo "✅ Python processes stopped"
fi

# Überprüfe ob Prozesse noch laufen
echo ""
echo "🔍 Checking for remaining processes..."
REMAINING=$(pgrep -f "trading\|main_simple\|npm.*dev\|vite" || true)
if [ ! -z "$REMAINING" ]; then
    echo "⚠️  Some processes are still running: $REMAINING"
    echo "You may need to kill them manually:"
    echo "kill -9 $REMAINING"
else
    echo "✅ All trading system processes stopped"
fi

echo ""
echo "🎉 Trading System stopped successfully!"
echo ""
echo "📋 To restart the system:"
echo "  ./scripts/start_system.sh"
echo "  or"
echo "  docker-compose up -d"

