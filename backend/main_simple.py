#!/usr/bin/env python3
"""
Trading System - Simplified Main Entry Point
"""

import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Trading System API",
        "version": "1.0.0",
        "components": {
            "data_collector": "active",
            "signal_generator": "active",
            "risk_manager": "active",
            "order_manager": "active",
            "security_manager": "active"
        }
    })

@app.route('/api/status', methods=['GET'])
def system_status():
    return jsonify({
        "status": "operational",
        "timestamp": "2025-09-01T08:00:00Z",
        "portfolio": {
            "total_value": 100000,
            "cash_balance": 95000,
            "risk_level": "LOW"
        },
        "trading": {
            "recent_orders": 0
        },
        "security": {
            "events_24h": 0
        }
    })

@app.route('/api/portfolio/status', methods=['GET'])
def portfolio_status():
    return jsonify({
        "status": "success",
        "portfolio": {
            "total_value": 100000,
            "cash_balance": 95000,
            "unrealized_pnl": 0,
            "realized_pnl": 0,
            "positions": [],
            "risk_metrics": {
                "portfolio_risk": "LOW",
                "max_drawdown": 0,
                "sharpe_ratio": 0
            }
        }
    })

@app.route('/api/signals/recommendations', methods=['GET'])
def get_recommendations():
    return jsonify({
        "status": "success",
        "recommendations": [
            {
                "symbol": "BTC-USD",
                "action": "HOLD",
                "strength": "WEAK",
                "confidence": 0.5,
                "price": 50000,
                "reasoning": "Demo mode - no live signals",
                "entry_price": 50000,
                "stop_loss": 48500,
                "take_profit": 52000
            }
        ],
        "count": 1,
        "timestamp": "2025-09-01T08:00:00Z"
    })

@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify({
        "status": "success",
        "orders": [],
        "count": 0
    })

if __name__ == '__main__':
    print("🚀 Starting Trading System API...")
    print("📊 API Base: http://localhost:5001" )
    print("✅ Demo mode - Basic endpoints active")
    print("")
    print("Available endpoints:")
    print("  GET /api/health")
    print("  GET /api/status") 
    print("  GET /api/portfolio/status")
    print("  GET /api/signals/recommendations")
    print("  GET /api/orders")
    print("")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=False
    )
