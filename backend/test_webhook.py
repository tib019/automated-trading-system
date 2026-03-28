#!/usr/bin/env python3
"""
Test-Script für TradingView Webhook Server
Demonstriert die Funktionalität des Webhook-Systems
"""

import requests
import json
import time
from datetime import datetime

def test_webhook_server():
    """Teste den Webhook-Server"""
    
    base_url = "http://localhost:5000"
    
    print("=" * 80)
 print(" WEBHOOK SERVER TEST")
    print("=" * 80)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
 print(f" Health Check: {data['status']}")
 print(f" Stats: {data['stats']['total_webhooks']} webhooks processed")
        else:
 print(f" Health Check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
 print(f" Health Check error: {e}")
 print(" Make sure the webhook server is running!")
        return
    
    # Test 2: Test Webhook
    print(f"\n2. Testing Test Webhook...")
    try:
        response = requests.post(f"{base_url}/webhook/test", timeout=5)
        if response.status_code == 200:
            data = response.json()
 print(f" Test Webhook: {data['success']}")
            if data['success']:
 print(f" Signal: {data['signal']['symbol']} {data['signal']['action']} @ ${data['signal']['price']}")
 print(f" Broker: {data['broker']}")
            else:
 print(f" Error: {data['error']}")
        else:
 print(f" Test Webhook failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
 print(f" Test Webhook error: {e}")
    
    # Test 3: Custom TradingView Alert
    print(f"\n3. Testing Custom TradingView Alert...")
    
    custom_alert = {
        "ticker": "ETH-USD",
        "action": "SELL",
        "price": 3500.00,
        "strength": "STRONG",
        "stop_loss": 3650.00,
        "take_profit": 3200.00,
        "position_size": 3.0,
        "message": "Strong bearish signal detected",
        "confidence_score": 0.9,
        "sentiment": -0.3,
        "technical_score": 0.7,
        "volume_score": 45
    }
    
    try:
        response = requests.post(
            f"{base_url}/webhook/tradingview",
            json=custom_alert,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
 print(f" Custom Alert: {data['success']}")
            if data['success']:
 print(f" Signal: {data['signal']['symbol']} {data['signal']['action']} @ ${data['signal']['price']}")
 print(f" Strength: {data['signal']['strength']}")
 print(f" Message: {data['message']}")
            else:
 print(f" Error: {data['error']}")
        else:
            data = response.json() if response.text else {}
 print(f" Custom Alert failed: {response.status_code}")
 print(f" Error: {data.get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
 print(f" Custom Alert error: {e}")
    
    # Test 4: Multiple Signals
    print(f"\n4. Testing Multiple Signals...")
    
    test_signals = [
        {
            "ticker": "BTC-USD",
            "action": "BUY",
            "price": 52000.00,
            "strength": "MODERATE",
            "message": "Bullish breakout"
        },
        {
            "ticker": "TSLA",
            "action": "SELL",
            "price": 250.00,
            "strength": "WEAK",
            "message": "Resistance level reached"
        },
        {
            "ticker": "AAPL",
            "action": "BUY",
            "price": 180.00,
            "strength": "STRONG",
            "message": "Earnings beat expected"
        }
    ]
    
    successful_signals = 0
    
    for i, signal in enumerate(test_signals, 1):
        try:
            response = requests.post(
                f"{base_url}/webhook/tradingview",
                json=signal,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    successful_signals += 1
 print(f" Signal {i}: {signal['ticker']} {signal['action']}")
                else:
 print(f" Signal {i} failed: {data['error']}")
            else:
 print(f" Signal {i} HTTP error: {response.status_code}")
            
            time.sleep(0.5)  # Kurze Pause zwischen Signalen
            
        except requests.exceptions.RequestException as e:
 print(f" Signal {i} error: {e}")
    
 print(f" Successfully processed: {successful_signals}/{len(test_signals)} signals")
    
    # Test 5: Status Check
    print(f"\n5. Checking Server Status...")
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            stats = data['webhook_stats']
            
 print(f" Webhook Statistics:")
            print(f"     Total Webhooks: {stats['total_webhooks']}")
            print(f"     Successful Orders: {stats['successful_orders']}")
            print(f"     Failed Orders: {stats['failed_orders']}")
            
            if stats['last_webhook']:
                print(f"     Last Webhook: {stats['last_webhook']}")
            
            # Broker Status
            broker_status = data['broker_status']
 print(f"\n Broker Status:")
            for broker, status in broker_status.items():
                connected = "✅" if status['connected'] else "❌"
                print(f"     {broker}: {connected}")
                
                if status['connected'] and status['balances']:
                    for asset, balance in list(status['balances'].items())[:3]:  # Zeige erste 3
                        if isinstance(balance, dict):
                            print(f"       {asset}: ${balance['total']:,.2f}")
                        else:
                            print(f"       {asset}: ${balance:,.2f}")
            
            # Recent Orders
            recent_orders = data['recent_orders']
            if recent_orders:
 print(f"\n Recent Orders ({len(recent_orders)}):")
                for order in recent_orders[:5]:  # Zeige erste 5
                    status_emoji = "✅" if order['status'] == 'FILLED' else "⏳" if order['status'] == 'SUBMITTED' else "❌"
                    print(f"     {status_emoji} {order['symbol']} {order['side']} {order['quantity']:.6f} @ ${order['price']:.2f}")
            
        else:
 print(f" Status check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
 print(f" Status check error: {e}")
    
    # Test 6: Order History
    print(f"\n6. Checking Order History...")
    try:
        response = requests.get(f"{base_url}/orders?limit=10", timeout=5)
        if response.status_code == 200:
            data = response.json()
            orders = data['orders']
            
 print(f" Order History ({data['total']} total):")
            
            if orders:
                for order in orders:
                    status_emoji = "✅" if order['status'] == 'FILLED' else "⏳" if order['status'] == 'SUBMITTED' else "❌"
                    created_time = datetime.fromisoformat(order['created_at']).strftime('%H:%M:%S')
                    
                    print(f"     {status_emoji} {created_time} | {order['symbol']} {order['side']} {order['quantity']:.6f} @ ${order['price']:.2f} | {order['broker']}")
                    
                    if order['error_message']:
 print(f" ️ Error: {order['error_message']}")
            else:
                print(f"     No orders found")
        else:
 print(f" Order history failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
 print(f" Order history error: {e}")
    
 print(f"\n WEBHOOK SERVER TEST COMPLETED!")
    print(f"=" * 80)

def create_sample_tradingview_alerts():
    """Erstelle Beispiel-TradingView-Alerts"""
    
 print(f"\n SAMPLE TRADINGVIEW ALERTS")
    print(f"=" * 80)
    print(f"Use these JSON payloads to test the webhook from TradingView:")
    
    samples = [
        {
            "name": "Bitcoin Buy Signal",
            "payload": {
                "ticker": "BTC-USD",
                "action": "BUY",
                "price": "{{close}}",
                "strength": "STRONG",
                "stop_loss": "{{close * 0.95}}",
                "take_profit": "{{close * 1.10}}",
                "position_size": 2.5,
                "message": "Golden cross detected on 4H chart",
                "confidence_score": 0.85
            }
        },
        {
            "name": "Ethereum Sell Signal",
            "payload": {
                "ticker": "ETH-USD",
                "action": "SELL",
                "price": "{{close}}",
                "strength": "MODERATE",
                "stop_loss": "{{close * 1.03}}",
                "take_profit": "{{close * 0.92}}",
                "position_size": 3.0,
                "message": "RSI overbought + resistance level",
                "confidence_score": 0.75
            }
        },
        {
            "name": "Stock Buy Signal",
            "payload": {
                "ticker": "AAPL",
                "action": "BUY",
                "price": "{{close}}",
                "strength": "WEAK",
                "stop_loss": "{{close * 0.97}}",
                "take_profit": "{{close * 1.06}}",
                "position_size": 1.5,
                "message": "Support bounce + volume increase",
                "confidence_score": 0.65
            }
        }
    ]
    
    for sample in samples:
        print(f"\n{sample['name']}:")
        print(f"URL: http://localhost:5000/webhook/tradingview")
        print(f"Method: POST")
        print(f"Content-Type: application/json")
        print(f"Body:")
        print(json.dumps(sample['payload'], indent=2))
        print(f"-" * 40)

if __name__ == "__main__":
    # Teste Webhook-Server
    test_webhook_server()
    
    # Zeige Beispiel-Alerts
    create_sample_tradingview_alerts()

