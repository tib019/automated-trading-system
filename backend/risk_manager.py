#!/usr/bin/env python3
"""
Trading System - Risk Management Module
Umfassendes Risikomanagement für automatisierte Trading-Entscheidungen
"""

import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from config import get_config
from signal_generator import TradingSignal, SignalType

# Logging Setup
logger = logging.getLogger(__name__)

class PositionStatus(Enum):
    """Status einer Trading-Position"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    STOPPED = "STOPPED"  # Stop-Loss ausgelöst
    PROFIT_TAKEN = "PROFIT_TAKEN"  # Take-Profit erreicht

class RiskLevel(Enum):
    """Risiko-Level des Portfolios"""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class Position:
    """Trading-Position-Datenklasse"""
    id: str
    symbol: str
    signal_type: SignalType
    entry_price: float
    current_price: float
    quantity: float
    position_size_usd: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    status: PositionStatus
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    max_drawdown: float = 0.0
    max_profit: float = 0.0

@dataclass
class PortfolioMetrics:
    """Portfolio-Metriken"""
    total_value: float
    cash_balance: float
    invested_amount: float
    total_pnl: float
    daily_pnl: float
    open_positions: int
    total_positions: int
    win_rate: float
    max_drawdown: float
    risk_level: RiskLevel

class PortfolioTracker:
    """Portfolio-Tracking und -Verwaltung"""
    
    def __init__(self, db_path: str = '/home/ubuntu/trading_system/trading_data.db'):
        self.db_path = db_path
        self.config = get_config()
        self.initial_capital = self.config.BACKTESTING['initial_capital']
        self.init_portfolio_database()
    
    def init_portfolio_database(self):
        """Initialisiere Portfolio-Datenbank-Tabellen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Positionen-Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    position_size_usd REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    entry_time DATETIME NOT NULL,
                    close_time DATETIME,
                    status TEXT NOT NULL,
                    unrealized_pnl REAL DEFAULT 0.0,
                    realized_pnl REAL DEFAULT 0.0,
                    max_drawdown REAL DEFAULT 0.0,
                    max_profit REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Portfolio-Historie-Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    total_value REAL NOT NULL,
                    cash_balance REAL NOT NULL,
                    invested_amount REAL NOT NULL,
                    total_pnl REAL NOT NULL,
                    daily_pnl REAL NOT NULL,
                    open_positions INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Risk-Events-Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS risk_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    action_taken TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Portfolio database initialized successfully")
    
    def open_position(self, signal: TradingSignal) -> str:
        """Öffne neue Position basierend auf Signal"""
        position_id = f"{signal.symbol}_{signal.signal_type.value}_{int(datetime.now().timestamp())}"
        
        # Berechne Positionsgröße in USD
        portfolio_value = self.get_portfolio_value()
        position_size_usd = portfolio_value * (signal.position_size_percent / 100)
        
        # Berechne Quantity basierend auf Entry-Preis
        quantity = position_size_usd / signal.entry_price
        
        position = Position(
            id=position_id,
            symbol=signal.symbol,
            signal_type=signal.signal_type,
            entry_price=signal.entry_price,
            current_price=signal.entry_price,
            quantity=quantity,
            position_size_usd=position_size_usd,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            entry_time=signal.timestamp,
            status=PositionStatus.OPEN
        )
        
        # Speichere in Datenbank
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO positions 
                (id, symbol, signal_type, entry_price, current_price, quantity, 
                 position_size_usd, stop_loss, take_profit, entry_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position.id, position.symbol, position.signal_type.value,
                position.entry_price, position.current_price, position.quantity,
                position.position_size_usd, position.stop_loss, position.take_profit,
                position.entry_time, position.status.value
            ))
            conn.commit()
        
        logger.info(f"Opened position: {position_id} for {signal.symbol}")
        return position_id
    
    def update_position_prices(self, symbol: str, current_price: float):
        """Update aktuelle Preise für alle offenen Positionen eines Symbols"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Hole alle offenen Positionen für Symbol
            cursor.execute('''
                SELECT * FROM positions 
                WHERE symbol = ? AND status = ?
            ''', (symbol, PositionStatus.OPEN.value))
            
            positions = cursor.fetchall()
            
            for pos_data in positions:
                position = self._row_to_position(pos_data)
                
                # Update aktuellen Preis
                position.current_price = current_price
                
                # Berechne PnL
                if position.signal_type == SignalType.BUY:
                    position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
                else:  # SELL
                    position.unrealized_pnl = (position.entry_price - current_price) * position.quantity
                
                # Update Max Profit/Drawdown
                if position.unrealized_pnl > position.max_profit:
                    position.max_profit = position.unrealized_pnl
                elif position.unrealized_pnl < 0 and abs(position.unrealized_pnl) > position.max_drawdown:
                    position.max_drawdown = abs(position.unrealized_pnl)
                
                # Prüfe Stop-Loss und Take-Profit
                should_close, close_reason = self._check_exit_conditions(position)
                
                if should_close:
                    self.close_position(position.id, close_reason, current_price)
                else:
                    # Update Position in Datenbank
                    cursor.execute('''
                        UPDATE positions 
                        SET current_price = ?, unrealized_pnl = ?, 
                            max_profit = ?, max_drawdown = ?
                        WHERE id = ?
                    ''', (
                        position.current_price, position.unrealized_pnl,
                        position.max_profit, position.max_drawdown, position.id
                    ))
            
            conn.commit()
    
    def _check_exit_conditions(self, position: Position) -> Tuple[bool, Optional[PositionStatus]]:
        """Prüfe ob Position geschlossen werden soll"""
        current_price = position.current_price
        
        if position.signal_type == SignalType.BUY:
            # Long Position
            if current_price <= position.stop_loss:
                return True, PositionStatus.STOPPED
            elif current_price >= position.take_profit:
                return True, PositionStatus.PROFIT_TAKEN
        else:
            # Short Position
            if current_price >= position.stop_loss:
                return True, PositionStatus.STOPPED
            elif current_price <= position.take_profit:
                return True, PositionStatus.PROFIT_TAKEN
        
        return False, None
    
    def close_position(self, position_id: str, status: PositionStatus, close_price: float):
        """Schließe Position"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Hole Position
            cursor.execute('SELECT * FROM positions WHERE id = ?', (position_id,))
            pos_data = cursor.fetchone()
            
            if not pos_data:
                logger.error(f"Position {position_id} not found")
                return
            
            position = self._row_to_position(pos_data)
            
            # Berechne finalen PnL
            if position.signal_type == SignalType.BUY:
                realized_pnl = (close_price - position.entry_price) * position.quantity
            else:
                realized_pnl = (position.entry_price - close_price) * position.quantity
            
            # Update Position
            cursor.execute('''
                UPDATE positions 
                SET status = ?, current_price = ?, realized_pnl = ?, 
                    close_time = ?, unrealized_pnl = 0
                WHERE id = ?
            ''', (
                status.value, close_price, realized_pnl, 
                datetime.now(), position_id
            ))
            
            conn.commit()
            
            logger.info(f"Closed position {position_id}: {status.value}, PnL: ${realized_pnl:.2f}")
    
    def get_open_positions(self) -> List[Position]:
        """Hole alle offenen Positionen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM positions WHERE status = ?
                ORDER BY entry_time DESC
            ''', (PositionStatus.OPEN.value,))
            
            return [self._row_to_position(row) for row in cursor.fetchall()]
    
    def get_portfolio_value(self) -> float:
        """Berechne aktuellen Portfolio-Wert"""
        open_positions = self.get_open_positions()
        
        # Investierter Betrag in offenen Positionen
        invested_amount = sum(pos.position_size_usd for pos in open_positions)
        
        # Unrealized PnL
        unrealized_pnl = sum(pos.unrealized_pnl for pos in open_positions)
        
        # Realized PnL aus geschlossenen Positionen
        realized_pnl = self.get_total_realized_pnl()
        
        # Cash Balance = Initial Capital - Invested + Realized PnL
        cash_balance = self.initial_capital - invested_amount + realized_pnl
        
        # Total Portfolio Value = Cash + Invested + Unrealized PnL
        total_value = cash_balance + invested_amount + unrealized_pnl
        
        return total_value
    
    def get_total_realized_pnl(self) -> float:
        """Hole gesamten realisierten PnL"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COALESCE(SUM(realized_pnl), 0) FROM positions 
                WHERE status IN (?, ?)
            ''', (PositionStatus.CLOSED.value, PositionStatus.STOPPED.value))
            
            result = cursor.fetchone()
            return result[0] if result else 0.0
    
    def get_portfolio_metrics(self) -> PortfolioMetrics:
        """Berechne umfassende Portfolio-Metriken"""
        open_positions = self.get_open_positions()
        
        # Grundlegende Werte
        total_value = self.get_portfolio_value()
        invested_amount = sum(pos.position_size_usd for pos in open_positions)
        cash_balance = total_value - invested_amount - sum(pos.unrealized_pnl for pos in open_positions)
        total_pnl = total_value - self.initial_capital
        
        # Täglicher PnL (vereinfacht)
        daily_pnl = sum(pos.unrealized_pnl for pos in open_positions)
        
        # Statistiken
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Gesamtanzahl Positionen
            cursor.execute('SELECT COUNT(*) FROM positions')
            total_positions = cursor.fetchone()[0]
            
            # Gewinnende Positionen
            cursor.execute('''
                SELECT COUNT(*) FROM positions 
                WHERE realized_pnl > 0 AND status IN (?, ?)
            ''', (PositionStatus.CLOSED.value, PositionStatus.PROFIT_TAKEN.value))
            winning_positions = cursor.fetchone()[0]
            
            # Win Rate
            win_rate = (winning_positions / max(1, total_positions - len(open_positions))) * 100
            
            # Max Drawdown (vereinfacht)
            cursor.execute('SELECT MIN(realized_pnl) FROM positions')
            max_loss = cursor.fetchone()[0] or 0
            max_drawdown = abs(max_loss) / self.initial_capital * 100
        
        # Risiko-Level bestimmen
        risk_level = self._calculate_risk_level(total_pnl, invested_amount, total_value)
        
        return PortfolioMetrics(
            total_value=total_value,
            cash_balance=cash_balance,
            invested_amount=invested_amount,
            total_pnl=total_pnl,
            daily_pnl=daily_pnl,
            open_positions=len(open_positions),
            total_positions=total_positions,
            win_rate=win_rate,
            max_drawdown=max_drawdown,
            risk_level=risk_level
        )
    
    def _calculate_risk_level(self, total_pnl: float, invested_amount: float, total_value: float) -> RiskLevel:
        """Berechne aktuelles Risiko-Level"""
        # PnL-basiertes Risiko
        pnl_percent = (total_pnl / self.initial_capital) * 100
        
        # Exposure-basiertes Risiko
        exposure_percent = (invested_amount / total_value) * 100
        
        # Kombiniertes Risiko
        if pnl_percent < -15 or exposure_percent > 80:
            return RiskLevel.CRITICAL
        elif pnl_percent < -10 or exposure_percent > 60:
            return RiskLevel.HIGH
        elif pnl_percent < -5 or exposure_percent > 40:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _row_to_position(self, row) -> Position:
        """Konvertiere Datenbank-Row zu Position-Objekt"""
        return Position(
            id=row[0],
            symbol=row[1],
            signal_type=SignalType(row[2]),
            entry_price=row[3],
            current_price=row[4],
            quantity=row[5],
            position_size_usd=row[6],
            stop_loss=row[7],
            take_profit=row[8],
            entry_time=datetime.fromisoformat(row[9]) if isinstance(row[9], str) else row[9],
            status=PositionStatus(row[11]),
            unrealized_pnl=row[12],
            realized_pnl=row[13],
            max_drawdown=row[14],
            max_profit=row[15]
        )

class RiskManager:
    """Hauptklasse für Risikomanagement"""
    
    def __init__(self):
        self.config = get_config()
        self.portfolio_tracker = PortfolioTracker()
        self.kill_switch_active = False
    
    def validate_signal(self, signal: TradingSignal) -> Tuple[bool, str]:
        """Validiere Trading-Signal gegen Risikomanagement-Regeln"""
        portfolio_metrics = self.portfolio_tracker.get_portfolio_metrics()
        
        # 1. Kill-Switch prüfen
        if self.kill_switch_active:
            return False, "Kill-Switch ist aktiv"
        
        # 2. Täglicher Verlust-Limit
        daily_loss_limit = self.config.RISK_MANAGEMENT['daily_loss_limit_percent']
        if portfolio_metrics.daily_pnl < -(portfolio_metrics.total_value * daily_loss_limit / 100):
            self.trigger_kill_switch("Daily loss limit exceeded")
            return False, f"Täglicher Verlust-Limit von {daily_loss_limit}% erreicht"
        
        # 3. Maximale offene Positionen
        max_positions = self.config.RISK_MANAGEMENT['max_open_positions']
        if portfolio_metrics.open_positions >= max_positions:
            return False, f"Maximale Anzahl offener Positionen ({max_positions}) erreicht"
        
        # 4. Portfolio-Exposure
        position_size_usd = portfolio_metrics.total_value * (signal.position_size_percent / 100)
        new_exposure = (portfolio_metrics.invested_amount + position_size_usd) / portfolio_metrics.total_value
        
        if new_exposure > 0.8:  # Max 80% Exposure
            return False, "Portfolio-Exposure würde 80% überschreiten"
        
        # 5. Symbol-Konzentration prüfen
        open_positions = self.portfolio_tracker.get_open_positions()
        symbol_exposure = sum(pos.position_size_usd for pos in open_positions if pos.symbol == signal.symbol)
        symbol_exposure_percent = (symbol_exposure + position_size_usd) / portfolio_metrics.total_value
        
        if symbol_exposure_percent > 0.2:  # Max 20% pro Symbol
            return False, f"Symbol-Konzentration für {signal.symbol} würde 20% überschreiten"
        
        # 6. Risiko-Level prüfen
        if portfolio_metrics.risk_level == RiskLevel.CRITICAL:
            return False, "Portfolio-Risiko ist CRITICAL - keine neuen Positionen"
        
        return True, "Signal validiert"
    
    def trigger_kill_switch(self, reason: str):
        """Aktiviere Kill-Switch und schließe alle Positionen"""
        self.kill_switch_active = True
        
        # Log Risk Event
        self._log_risk_event("KILL_SWITCH", reason, "CRITICAL", "All positions closed")
        
        # Schließe alle offenen Positionen
        open_positions = self.portfolio_tracker.get_open_positions()
        
        for position in open_positions:
            # Simuliere Marktpreis-Schließung
            self.portfolio_tracker.close_position(
                position.id, 
                PositionStatus.CLOSED, 
                position.current_price
            )
        
        logger.critical(f"KILL-SWITCH ACTIVATED: {reason}")
    
    def deactivate_kill_switch(self, reason: str = "Manual override"):
        """Deaktiviere Kill-Switch"""
        self.kill_switch_active = False
        self._log_risk_event("KILL_SWITCH_DEACTIVATED", reason, "INFO", "Trading resumed")
        logger.info(f"Kill-Switch deactivated: {reason}")
    
    def monitor_portfolio(self) -> Dict[str, any]:
        """Kontinuierliche Portfolio-Überwachung"""
        portfolio_metrics = self.portfolio_tracker.get_portfolio_metrics()
        
        alerts = []
        actions_taken = []
        
        # 1. Verlust-Überwachung
        total_loss_percent = (portfolio_metrics.total_pnl / self.config.BACKTESTING['initial_capital']) * 100
        
        if total_loss_percent < -15:
            if not self.kill_switch_active:
                self.trigger_kill_switch(f"Total loss exceeded -15% ({total_loss_percent:.1f}%)")
                actions_taken.append("Kill-Switch activated")
        elif total_loss_percent < -10:
            alerts.append(f"WARNING: Portfolio loss at {total_loss_percent:.1f}%")
        
        # 2. Risiko-Level-Überwachung
        if portfolio_metrics.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            alerts.append(f"Portfolio risk level: {portfolio_metrics.risk_level.value}")
        
        # 3. Position-Überwachung
        open_positions = self.portfolio_tracker.get_open_positions()
        for position in open_positions:
            loss_percent = (position.unrealized_pnl / position.position_size_usd) * 100
            if loss_percent < -10:  # Position verliert mehr als 10%
                alerts.append(f"{position.symbol}: Position loss {loss_percent:.1f}%")
        
        # 4. Speichere Portfolio-Historie
        self._save_portfolio_snapshot(portfolio_metrics)
        
        return {
            'portfolio_metrics': asdict(portfolio_metrics),
            'alerts': alerts,
            'actions_taken': actions_taken,
            'kill_switch_active': self.kill_switch_active,
            'timestamp': datetime.now()
        }
    
    def _log_risk_event(self, event_type: str, description: str, severity: str, action_taken: str = None):
        """Logge Risiko-Event in Datenbank"""
        with sqlite3.connect(self.portfolio_tracker.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO risk_events (timestamp, event_type, description, severity, action_taken)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now(), event_type, description, severity, action_taken))
            conn.commit()
    
    def _save_portfolio_snapshot(self, metrics: PortfolioMetrics):
        """Speichere Portfolio-Snapshot für Historie"""
        with sqlite3.connect(self.portfolio_tracker.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO portfolio_history 
                (timestamp, total_value, cash_balance, invested_amount, total_pnl, 
                 daily_pnl, open_positions, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(), metrics.total_value, metrics.cash_balance,
                metrics.invested_amount, metrics.total_pnl, metrics.daily_pnl,
                metrics.open_positions, metrics.risk_level.value
            ))
            conn.commit()

def main():
    """Test des Risikomanagement-Systems"""
    print("=" * 80)
    print("RISK MANAGEMENT SYSTEM TEST")
    print("=" * 80)
    
    risk_manager = RiskManager()
    portfolio_tracker = risk_manager.portfolio_tracker
    
    # Simuliere einige Positionen
    from signal_generator import TradingSignal, SignalType, SignalStrength
    
    # Test-Signal 1: BTC Long
    test_signal_1 = TradingSignal(
        symbol="BTC-USD",
        timestamp=datetime.now(),
        signal_type=SignalType.BUY,
        strength=SignalStrength.STRONG,
        entry_price=108400.99,
        stop_loss=105000.00,
        take_profit=115000.00,
        confidence=0.85,
        reasoning="Test signal",
        sentiment_score=0.7,
        technical_score=0.6,
        volume_score=50,
        position_size_percent=2.0,
        risk_reward_ratio=2.0
    )
    
    # Validiere und öffne Position
    is_valid, reason = risk_manager.validate_signal(test_signal_1)
    print(f"Signal Validation: {'' if is_valid else ''} {reason}")
    
    if is_valid:
        position_id = portfolio_tracker.open_position(test_signal_1)
        print(f"Position opened: {position_id}")
    
    # Update Preise (simuliere Marktbewegung)
    portfolio_tracker.update_position_prices("BTC-USD", 110000.00)  # Gewinn
    
    # Portfolio-Monitoring
    monitoring_result = risk_manager.monitor_portfolio()
    
    print(f"\n PORTFOLIO METRICS:")
    metrics = monitoring_result['portfolio_metrics']
    print(f"   Total Value: ${metrics['total_value']:,.2f}")
    print(f"   Cash Balance: ${metrics['cash_balance']:,.2f}")
    print(f"   Invested: ${metrics['invested_amount']:,.2f}")
    print(f"   Total PnL: ${metrics['total_pnl']:+,.2f}")
    print(f"   Open Positions: {metrics['open_positions']}")
    print(f"   Win Rate: {metrics['win_rate']:.1f}%")
    print(f"   Risk Level: {metrics['risk_level']}")
    
    if monitoring_result['alerts']:
        print(f"\n ALERTS:")
        for alert in monitoring_result['alerts']:
            print(f"   - {alert}")

    if monitoring_result['actions_taken']:
        print(f"\n ACTIONS TAKEN:")
        for action in monitoring_result['actions_taken']:
            print(f"   - {action}")

    # Zeige offene Positionen
    open_positions = portfolio_tracker.get_open_positions()
    if open_positions:
        print(f"\n OPEN POSITIONS:")
        for pos in open_positions:
            pnl_percent = (pos.unrealized_pnl / pos.position_size_usd) * 100
            print(f"   {pos.symbol}: ${pos.unrealized_pnl:+,.2f} ({pnl_percent:+.1f}%)")

if __name__ == "__main__":
    main()

