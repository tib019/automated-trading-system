#!/usr/bin/env python3
"""
Trading System - Order Management Module
Umfassendes Order-Management für verschiedene Broker-Integrationen
"""

import sqlite3
import logging
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import hmac
import base64

from config import get_config
from signal_generator import TradingSignal, SignalType
from risk_manager import RiskManager

# Logging Setup
logger = logging.getLogger(__name__)

class OrderType(Enum):
    """Order-Typen"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class OrderStatus(Enum):
    """Order-Status"""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class BrokerType(Enum):
    """Unterstützte Broker"""
    BINANCE = "BINANCE"
    INTERACTIVE_BROKERS = "INTERACTIVE_BROKERS"
    TRADINGVIEW = "TRADINGVIEW"
    PAPER_TRADING = "PAPER_TRADING"

@dataclass
class Order:
    """Order-Datenklasse"""
    id: str
    broker_order_id: Optional[str]
    symbol: str
    order_type: OrderType
    side: SignalType
    quantity: float
    price: Optional[float]
    stop_price: Optional[float]
    status: OrderStatus
    broker: BrokerType
    created_at: datetime
    updated_at: datetime
    filled_quantity: float = 0.0
    avg_fill_price: Optional[float] = None
    commission: float = 0.0
    error_message: Optional[str] = None

class BrokerInterface:
    """Basis-Interface für Broker-Integrationen"""
    
    def __init__(self, broker_type: BrokerType, config: Dict):
        self.broker_type = broker_type
        self.config = config
        self.is_connected = False
    
    def connect(self) -> bool:
        """Verbinde mit Broker"""
        raise NotImplementedError
    
    def disconnect(self):
        """Trenne Verbindung"""
        raise NotImplementedError
    
    def submit_order(self, order: Order) -> Tuple[bool, str]:
        """Sende Order an Broker"""
        raise NotImplementedError
    
    def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """Storniere Order"""
        raise NotImplementedError
    
    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """Hole Order-Status"""
        raise NotImplementedError
    
    def get_account_balance(self) -> Dict[str, float]:
        """Hole Account-Balance"""
        raise NotImplementedError
    
    def get_positions(self) -> List[Dict]:
        """Hole aktuelle Positionen"""
        raise NotImplementedError

class BinanceInterface(BrokerInterface):
    """Binance API Integration"""
    
    def __init__(self, config: Dict):
        super().__init__(BrokerType.BINANCE, config)
        self.api_key = config.get('api_key', '')
        self.api_secret = config.get('api_secret', '')
        self.base_url = config.get('base_url', 'https://api.binance.com')
        self.testnet = config.get('testnet', True)
        
        if self.testnet:
            self.base_url = 'https://testnet.binance.vision'
    
    def connect(self) -> bool:
        """Teste Binance-Verbindung"""
        try:
            response = self._make_request('GET', '/api/v3/time')
            if response and 'serverTime' in response:
                self.is_connected = True
                logger.info("Connected to Binance API")
                return True
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")
        
        self.is_connected = False
        return False
    
    def disconnect(self):
        """Trenne Binance-Verbindung"""
        self.is_connected = False
        logger.info("Disconnected from Binance API")
    
    def submit_order(self, order: Order) -> Tuple[bool, str]:
        """Sende Order an Binance"""
        if not self.is_connected:
            return False, "Not connected to Binance"
        
        try:
            # Konvertiere Order-Parameter
            params = {
                'symbol': order.symbol.replace('-', ''),  # BTC-USD -> BTCUSD
                'side': 'BUY' if order.side == SignalType.BUY else 'SELL',
                'type': order.order_type.value,
                'quantity': order.quantity,
                'timestamp': int(time.time() * 1000)
            }
            
            if order.order_type == OrderType.LIMIT:
                params['price'] = order.price
                params['timeInForce'] = 'GTC'  # Good Till Cancelled
            
            if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
                params['stopPrice'] = order.stop_price
            
            # Sende Order
            response = self._make_request('POST', '/api/v3/order', params, signed=True)
            
            if response and 'orderId' in response:
                order.broker_order_id = str(response['orderId'])
                order.status = OrderStatus.SUBMITTED
                return True, f"Order submitted: {order.broker_order_id}"
            else:
                error_msg = response.get('msg', 'Unknown error') if response else 'No response'
                return False, f"Order failed: {error_msg}"
                
        except Exception as e:
            logger.error(f"Error submitting Binance order: {e}")
            return False, f"Exception: {str(e)}"
    
    def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """Storniere Binance-Order"""
        try:
            params = {
                'orderId': order_id,
                'timestamp': int(time.time() * 1000)
            }
            
            response = self._make_request('DELETE', '/api/v3/order', params, signed=True)
            
            if response and response.get('status') == 'CANCELED':
                return True, "Order cancelled successfully"
            else:
                return False, f"Cancel failed: {response.get('msg', 'Unknown error')}"
                
        except Exception as e:
            return False, f"Exception: {str(e)}"
    
    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """Hole Binance-Order-Status"""
        try:
            params = {
                'orderId': order_id,
                'timestamp': int(time.time() * 1000)
            }
            
            response = self._make_request('GET', '/api/v3/order', params, signed=True)
            
            if response:
                status_map = {
                    'NEW': OrderStatus.SUBMITTED,
                    'PARTIALLY_FILLED': OrderStatus.PARTIALLY_FILLED,
                    'FILLED': OrderStatus.FILLED,
                    'CANCELED': OrderStatus.CANCELLED,
                    'REJECTED': OrderStatus.REJECTED,
                    'EXPIRED': OrderStatus.EXPIRED
                }
                return status_map.get(response.get('status'), OrderStatus.PENDING)
                
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
        
        return None
    
    def get_account_balance(self) -> Dict[str, float]:
        """Hole Binance-Account-Balance"""
        try:
            params = {'timestamp': int(time.time() * 1000)}
            response = self._make_request('GET', '/api/v3/account', params, signed=True)
            
            if response and 'balances' in response:
                balances = {}
                for balance in response['balances']:
                    asset = balance['asset']
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    if free > 0 or locked > 0:
                        balances[asset] = {'free': free, 'locked': locked, 'total': free + locked}
                return balances
                
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
        
        return {}
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Optional[Dict]:
        """Mache HTTP-Request an Binance API"""
        url = self.base_url + endpoint
        headers = {'X-MBX-APIKEY': self.api_key} if self.api_key else {}
        
        if params is None:
            params = {}
        
        if signed and self.api_secret:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            params['signature'] = signature
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, data=params, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, timeout=10)
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Binance API error: {response.status_code} - {response.text}")
                return response.json() if response.text else None
                
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

class PaperTradingInterface(BrokerInterface):
    """Paper Trading Interface für Tests"""
    
    def __init__(self, config: Dict):
        super().__init__(BrokerType.PAPER_TRADING, config)
        self.initial_balance = config.get('initial_balance', 100000)
        self.balances = {'USD': self.initial_balance}
        self.positions = {}
        self.orders = {}
        self.commission_rate = config.get('commission_rate', 0.001)  # 0.1%
    
    def connect(self) -> bool:
        """Paper Trading ist immer verbunden"""
        self.is_connected = True
        logger.info("Connected to Paper Trading")
        return True
    
    def disconnect(self):
        """Trenne Paper Trading"""
        self.is_connected = False
        logger.info("Disconnected from Paper Trading")
    
    def submit_order(self, order: Order) -> Tuple[bool, str]:
        """Simuliere Order-Ausführung"""
        if not self.is_connected:
            return False, "Not connected"
        
        try:
            # Generiere Broker-Order-ID
            order.broker_order_id = f"PAPER_{int(time.time() * 1000)}"
            
            # Simuliere sofortige Ausführung bei Market Orders
            if order.order_type == OrderType.MARKET:
                # Simuliere aktuellen Marktpreis (vereinfacht)
                market_price = order.price if order.price else 100.0
                
                # Berechne Order-Wert
                order_value = order.quantity * market_price
                commission = order_value * self.commission_rate
                
                # Prüfe verfügbare Balance
                if order.side == SignalType.BUY:
                    required_balance = order_value + commission
                    if self.balances.get('USD', 0) < required_balance:
                        order.status = OrderStatus.REJECTED
                        order.error_message = "Insufficient balance"
                        return False, "Insufficient balance"
                    
                    # Führe Kauf aus
                    self.balances['USD'] -= required_balance
                    symbol_base = order.symbol.split('-')[0]
                    self.balances[symbol_base] = self.balances.get(symbol_base, 0) + order.quantity
                    
                else:  # SELL
                    symbol_base = order.symbol.split('-')[0]
                    if self.balances.get(symbol_base, 0) < order.quantity:
                        order.status = OrderStatus.REJECTED
                        order.error_message = "Insufficient position"
                        return False, "Insufficient position"
                    
                    # Führe Verkauf aus
                    self.balances[symbol_base] -= order.quantity
                    self.balances['USD'] += order_value - commission
                
                # Update Order
                order.status = OrderStatus.FILLED
                order.filled_quantity = order.quantity
                order.avg_fill_price = market_price
                order.commission = commission
                
                # Speichere Order
                self.orders[order.broker_order_id] = order
                
                return True, f"Paper order filled at ${market_price:.2f}"
            
            else:
                # Limit/Stop Orders werden als submitted markiert
                order.status = OrderStatus.SUBMITTED
                self.orders[order.broker_order_id] = order
                return True, f"Paper order submitted: {order.broker_order_id}"
                
        except Exception as e:
            logger.error(f"Error in paper trading order: {e}")
            return False, f"Exception: {str(e)}"
    
    def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """Storniere Paper Trading Order"""
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status in [OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED]:
                order.status = OrderStatus.CANCELLED
                return True, "Paper order cancelled"
            else:
                return False, f"Cannot cancel order in status: {order.status.value}"
        else:
            return False, "Order not found"
    
    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """Hole Paper Trading Order-Status"""
        if order_id in self.orders:
            return self.orders[order_id].status
        return None
    
    def get_account_balance(self) -> Dict[str, float]:
        """Hole Paper Trading Balance"""
        return {asset: {'free': balance, 'locked': 0.0, 'total': balance} 
                for asset, balance in self.balances.items() if balance > 0}
    
    def get_positions(self) -> List[Dict]:
        """Hole Paper Trading Positionen"""
        positions = []
        for asset, quantity in self.balances.items():
            if asset != 'USD' and quantity > 0:
                positions.append({
                    'symbol': f"{asset}-USD",
                    'quantity': quantity,
                    'side': 'LONG',
                    'avg_price': 100.0,  # Vereinfacht
                    'unrealized_pnl': 0.0
                })
        return positions

class OrderManager:
    """Hauptklasse für Order-Management"""
    
    def __init__(self):
        self.config = get_config()
        self.risk_manager = RiskManager()
        self.brokers = {}
        self.db_path = '/home/ubuntu/trading_system/trading_data.db'
        
        # Initialisiere Datenbank
        self._init_order_database()
        
        # Lade Broker-Konfigurationen
        self._load_broker_configs()
    
    def _init_order_database(self):
        """Initialisiere Order-Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    broker_order_id TEXT,
                    symbol TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL,
                    stop_price REAL,
                    status TEXT NOT NULL,
                    broker TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    filled_quantity REAL DEFAULT 0.0,
                    avg_fill_price REAL,
                    commission REAL DEFAULT 0.0,
                    error_message TEXT
                )
            ''')
            conn.commit()
            logger.info("Order database initialized")
    
    def _load_broker_configs(self):
        """Lade Broker-Konfigurationen"""
        # Paper Trading (immer verfügbar)
        paper_config = {
            'initial_balance': 100000,
            'commission_rate': 0.001
        }
        self.brokers[BrokerType.PAPER_TRADING] = PaperTradingInterface(paper_config)
        
        # Binance (falls konfiguriert)
        binance_config = self.config.BROKER_CONFIG.get('binance', {})
        if binance_config.get('enabled', False):
            self.brokers[BrokerType.BINANCE] = BinanceInterface(binance_config)
        
        logger.info(f"Loaded {len(self.brokers)} broker interfaces")
    
    def connect_brokers(self) -> Dict[BrokerType, bool]:
        """Verbinde mit allen konfigurierten Brokern"""
        results = {}
        
        for broker_type, broker_interface in self.brokers.items():
            try:
                success = broker_interface.connect()
                results[broker_type] = success
                logger.info(f"Broker {broker_type.value}: {'Connected' if success else 'Failed'}")
            except Exception as e:
                results[broker_type] = False
                logger.error(f"Error connecting to {broker_type.value}: {e}")
        
        return results
    
    def execute_signal(self, signal: TradingSignal, broker_type: BrokerType = BrokerType.PAPER_TRADING) -> Tuple[bool, str]:
        """Führe Trading-Signal aus"""
        
        # Validiere Signal mit Risikomanagement
        is_valid, validation_message = self.risk_manager.validate_signal(signal)
        if not is_valid:
            logger.warning(f"Signal validation failed: {validation_message}")
            return False, f"Risk validation failed: {validation_message}"
        
        # Prüfe Broker-Verfügbarkeit
        if broker_type not in self.brokers:
            return False, f"Broker {broker_type.value} not configured"
        
        broker = self.brokers[broker_type]
        if not broker.is_connected:
            return False, f"Broker {broker_type.value} not connected"
        
        # Erstelle Order
        order = Order(
            id=f"ORDER_{int(time.time() * 1000)}",
            broker_order_id=None,
            symbol=signal.symbol,
            order_type=OrderType.MARKET,  # Vereinfacht für Demo
            side=signal.signal_type,
            quantity=self._calculate_quantity(signal, broker),
            price=signal.entry_price,
            stop_price=None,
            status=OrderStatus.PENDING,
            broker=broker_type,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Sende Order an Broker
        success, message = broker.submit_order(order)
        
        if success:
            # Speichere Order in Datenbank
            self._save_order(order)
            
            # Öffne Position im Portfolio-Tracker
            if order.status == OrderStatus.FILLED:
                self.risk_manager.portfolio_tracker.open_position(signal)
            
            logger.info(f"Order executed successfully: {order.id}")
        else:
            order.status = OrderStatus.REJECTED
            order.error_message = message
            self._save_order(order)
            logger.error(f"Order execution failed: {message}")
        
        return success, message
    
    def _calculate_quantity(self, signal: TradingSignal, broker: BrokerInterface) -> float:
        """Berechne Order-Quantity basierend auf Position-Size"""
        
        # Hole Account-Balance
        balances = broker.get_account_balance()
        
        # Berechne verfügbares Kapital
        if 'USD' in balances:
            available_capital = balances['USD'].get('free', 0)
        else:
            available_capital = 100000  # Fallback für Paper Trading
        
        # Berechne Position-Size
        position_size_usd = available_capital * (signal.position_size_percent / 100)
        
        # Berechne Quantity
        quantity = position_size_usd / signal.entry_price
        
        # Runde auf sinnvolle Dezimalstellen
        if signal.symbol.startswith('BTC'):
            return round(quantity, 6)
        elif signal.symbol.startswith('ETH'):
            return round(quantity, 4)
        else:
            return round(quantity, 2)
    
    def _save_order(self, order: Order):
        """Speichere Order in Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO orders 
                (id, broker_order_id, symbol, order_type, side, quantity, price, stop_price,
                 status, broker, created_at, updated_at, filled_quantity, avg_fill_price, 
                 commission, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order.id, order.broker_order_id, order.symbol, order.order_type.value,
                order.side.value, order.quantity, order.price, order.stop_price,
                order.status.value, order.broker.value, order.created_at, order.updated_at,
                order.filled_quantity, order.avg_fill_price, order.commission, order.error_message
            ))
            conn.commit()
    
    def get_order_history(self, limit: int = 50) -> List[Order]:
        """Hole Order-Historie"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM orders 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            orders = []
            for row in cursor.fetchall():
                order = Order(
                    id=row[0],
                    broker_order_id=row[1],
                    symbol=row[2],
                    order_type=OrderType(row[3]),
                    side=SignalType(row[4]),
                    quantity=row[5],
                    price=row[6],
                    stop_price=row[7],
                    status=OrderStatus(row[8]),
                    broker=BrokerType(row[9]),
                    created_at=datetime.fromisoformat(row[10]) if isinstance(row[10], str) else row[10],
                    updated_at=datetime.fromisoformat(row[11]) if isinstance(row[11], str) else row[11],
                    filled_quantity=row[12],
                    avg_fill_price=row[13],
                    commission=row[14],
                    error_message=row[15]
                )
                orders.append(order)
            
            return orders
    
    def get_broker_status(self) -> Dict[str, Dict]:
        """Hole Status aller Broker"""
        status = {}
        
        for broker_type, broker in self.brokers.items():
            try:
                balances = broker.get_account_balance() if broker.is_connected else {}
                positions = broker.get_positions() if broker.is_connected else []
                
                status[broker_type.value] = {
                    'connected': broker.is_connected,
                    'balances': balances,
                    'positions': positions,
                    'position_count': len(positions)
                }
            except Exception as e:
                status[broker_type.value] = {
                    'connected': False,
                    'error': str(e),
                    'balances': {},
                    'positions': [],
                    'position_count': 0
                }
        
        return status

def main():
    """Test des Order-Management-Systems"""
    print("=" * 80)
    print("📋 ORDER MANAGEMENT SYSTEM TEST")
    print("=" * 80)
    
    order_manager = OrderManager()
    
    # Verbinde mit Brokern
    print("🔌 Connecting to brokers...")
    connection_results = order_manager.connect_brokers()
    
    for broker_type, connected in connection_results.items():
        status = "✅ Connected" if connected else "❌ Failed"
        print(f"   {broker_type.value}: {status}")
    
    # Hole Broker-Status
    print(f"\n📊 Broker Status:")
    broker_status = order_manager.get_broker_status()
    
    for broker_name, status in broker_status.items():
        print(f"\n{broker_name}:")
        print(f"   Connected: {'✅' if status['connected'] else '❌'}")
        
        if status['connected']:
            balances = status['balances']
            if balances:
                print(f"   Balances:")
                for asset, balance in balances.items():
                    if isinstance(balance, dict):
                        print(f"     {asset}: ${balance['total']:,.2f}")
                    else:
                        print(f"     {asset}: ${balance:,.2f}")
            
            positions = status['positions']
            if positions:
                print(f"   Positions: {len(positions)}")
                for pos in positions[:3]:  # Zeige erste 3
                    print(f"     {pos['symbol']}: {pos['quantity']} ({pos['side']})")
            else:
                print(f"   Positions: None")
    
    # Test Order-Ausführung mit Paper Trading
    print(f"\n📋 Testing order execution...")
    
    from signal_generator import TradingSignal, SignalStrength
    
    test_signal = TradingSignal(
        symbol="BTC-USD",
        timestamp=datetime.now(),
        signal_type=SignalType.BUY,
        strength=SignalStrength.MODERATE,
        entry_price=50000.00,
        stop_loss=48000.00,
        take_profit=55000.00,
        confidence=0.75,
        reasoning="Test order execution",
        sentiment_score=0.5,
        technical_score=0.6,
        volume_score=25,
        position_size_percent=2.0,
        risk_reward_ratio=2.5
    )
    
    success, message = order_manager.execute_signal(test_signal, BrokerType.PAPER_TRADING)
    
    if success:
        print(f"✅ Test order executed: {message}")
    else:
        print(f"❌ Test order failed: {message}")
    
    # Zeige Order-Historie
    print(f"\n📋 Order History:")
    orders = order_manager.get_order_history(5)
    
    if orders:
        for order in orders:
            status_emoji = "✅" if order.status == OrderStatus.FILLED else "⏳" if order.status == OrderStatus.SUBMITTED else "❌"
            print(f"   {status_emoji} {order.symbol} {order.side.value} {order.quantity:.6f} @ ${order.price:.2f} - {order.status.value}")
    else:
        print("   No orders found")
    
    print(f"\n✅ Order Management System test completed!")

if __name__ == "__main__":
    main()

