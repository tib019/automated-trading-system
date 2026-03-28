#!/usr/bin/env python3
"""
Trading System - Backtesting Engine
Umfassendes Framework für Strategie-Backtesting mit historischen Daten
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json

from config import get_config
from signal_generator import SignalGenerator, TradingSignal, SignalType, SignalStrength
from sentiment_analyzer import SentimentAggregator
from risk_manager import PortfolioTracker, Position, PositionStatus

@dataclass
class BacktestResult:
    """Backtesting-Ergebnis-Datenklasse"""
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_percent: float
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    avg_trade_duration: float
    volatility: float
    calmar_ratio: float

@dataclass
class BacktestTrade:
    """Einzelner Backtest-Trade"""
    symbol: str
    entry_time: datetime
    exit_time: datetime
    signal_type: SignalType
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_percent: float
    duration_hours: float
    exit_reason: str

class HistoricalDataManager:
    """Manager für historische Marktdaten"""
    
    def __init__(self, db_path: str = '/home/ubuntu/trading_system/trading_data.db'):
        self.db_path = db_path
        self.config = get_config()
    
    def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Hole historische Marktdaten für Symbol"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT timestamp, open_price, high_price, low_price, close_price, volume
                FROM market_data 
                WHERE symbol = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
            
            if df.empty:
                return df
            
            # Konvertiere Timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Berechne zusätzliche Indikatoren
            df['returns'] = df['close_price'].pct_change()
            df['sma_20'] = df['close_price'].rolling(window=20).mean()
            df['sma_50'] = df['close_price'].rolling(window=50).mean()
            df['volatility'] = df['returns'].rolling(window=20).std()
            
            return df
    
    def get_historical_sentiment(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Hole historische Sentiment-Daten"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT timestamp, sentiment_score, source, engagement
                FROM sentiment_data 
                WHERE symbol = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
            
            if df.empty:
                return df
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Aggregiere Sentiment pro Tag
            daily_sentiment = df.groupby(df.index.date).agg({
                'sentiment_score': 'mean',
                'engagement': 'sum'
            })
            
            return daily_sentiment

class BacktestingEngine:
    """Hauptklasse für Backtesting"""
    
    def __init__(self):
        self.config = get_config()
        self.data_manager = HistoricalDataManager()
        self.signal_generator = SignalGenerator()
        
        # Backtesting-Parameter
        self.initial_capital = self.config.BACKTESTING['initial_capital']
        self.commission = 0.001  # 0.1% Kommission
        self.slippage = 0.0005   # 0.05% Slippage
        
    def run_backtest(self, symbols: List[str], start_date: datetime, end_date: datetime, 
                    strategy_name: str = "Default Strategy") -> BacktestResult:
        """Führe Backtest für gegebene Symbole und Zeitraum durch"""
        
 print(f" Starting backtest: {strategy_name}")
        print(f"   Period: {start_date.date()} to {end_date.date()}")
        print(f"   Symbols: {', '.join(symbols)}")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        
        # Portfolio-Initialisierung
        portfolio = {
            'cash': self.initial_capital,
            'positions': {},
            'portfolio_value': self.initial_capital,
            'daily_values': [],
            'trades': []
        }
        
        # Hole historische Daten für alle Symbole
        historical_data = {}
        for symbol in symbols:
            data = self.data_manager.get_historical_data(symbol, start_date, end_date)
            if not data.empty:
                historical_data[symbol] = data
                print(f"   Loaded {len(data)} data points for {symbol}")
        
        if not historical_data:
            raise ValueError("No historical data available for backtesting")
        
        # Erstelle gemeinsamen Zeitindex
        all_dates = set()
        for data in historical_data.values():
            all_dates.update(data.index)
        
        all_dates = sorted(all_dates)
        
        # Simuliere Trading Tag für Tag
        for current_date in all_dates:
            self._process_trading_day(current_date, historical_data, portfolio)
        
        # Berechne finale Metriken
        result = self._calculate_backtest_metrics(portfolio, strategy_name, start_date, end_date)
        
 print(f" Backtest completed!")
        print(f"   Final Capital: ${result.final_capital:,.2f}")
        print(f"   Total Return: {result.total_return_percent:+.2f}%")
        print(f"   Total Trades: {result.total_trades}")
        print(f"   Win Rate: {result.win_rate:.1f}%")
        
        return result
    
    def _process_trading_day(self, current_date: datetime, historical_data: Dict[str, pd.DataFrame], 
                           portfolio: Dict):
        """Verarbeite einen Trading-Tag"""
        
        # Update Portfolio-Wert
        portfolio_value = portfolio['cash']
        
        # Update offene Positionen
        positions_to_close = []
        
        for symbol, position in portfolio['positions'].items():
            if symbol in historical_data and current_date in historical_data[symbol].index:
                current_price = historical_data[symbol].loc[current_date, 'close_price']
                
                # Update Position-Wert
                position['current_price'] = current_price
                position['unrealized_pnl'] = self._calculate_position_pnl(position, current_price)
                portfolio_value += position['position_value'] + position['unrealized_pnl']
                
                # Prüfe Exit-Bedingungen
                should_exit, exit_reason = self._check_exit_conditions(position, current_price, current_date)
                
                if should_exit:
                    positions_to_close.append((symbol, exit_reason))
        
        # Schließe Positionen
        for symbol, exit_reason in positions_to_close:
            self._close_position(symbol, portfolio, current_date, exit_reason)
        
        # Generiere neue Signale
        for symbol in historical_data.keys():
            if symbol not in portfolio['positions'] and current_date in historical_data[symbol].index:
                # Simuliere Signal-Generierung mit historischen Daten
                signal = self._generate_historical_signal(symbol, current_date, historical_data[symbol])
                
                if signal and self._validate_signal(signal, portfolio):
                    self._open_position(signal, portfolio, current_date)
        
        # Speichere täglichen Portfolio-Wert
        portfolio['portfolio_value'] = portfolio_value
        portfolio['daily_values'].append({
            'date': current_date,
            'value': portfolio_value,
            'cash': portfolio['cash'],
            'positions_count': len(portfolio['positions'])
        })
    
    def _generate_historical_signal(self, symbol: str, date: datetime, data: pd.DataFrame) -> Optional[TradingSignal]:
        """Generiere Signal basierend auf historischen Daten"""
        
        # Brauche mindestens 50 Datenpunkte für technische Analyse
        if len(data.loc[:date]) < 50:
            return None
        
        # Hole Daten bis zum aktuellen Datum
        historical_slice = data.loc[:date].tail(50)
        current_price = data.loc[date, 'close_price']
        
        # Einfache technische Signale
        sma_20 = historical_slice['close_price'].rolling(20).mean().iloc[-1]
        sma_50 = historical_slice['close_price'].rolling(50).mean().iloc[-1]
        
        # RSI berechnen
        delta = historical_slice['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Signal-Logik
        signal_score = 0.0
        
        # Moving Average Signal
        if sma_20 > sma_50:
            signal_score += 0.3
        else:
            signal_score -= 0.3
        
        # RSI Signal
        if current_rsi < 30:  # Oversold
            signal_score += 0.4
        elif current_rsi > 70:  # Overbought
            signal_score -= 0.4
        
        # Preis vs. SMA
        if current_price > sma_20:
            signal_score += 0.2
        else:
            signal_score -= 0.2
        
        # Generiere Signal wenn Score stark genug
        if signal_score > 0.5:
            signal_type = SignalType.BUY
            strength = SignalStrength.STRONG if signal_score > 0.7 else SignalStrength.MODERATE
        elif signal_score < -0.5:
            signal_type = SignalType.SELL
            strength = SignalStrength.STRONG if signal_score < -0.7 else SignalStrength.MODERATE
        else:
            return None
        
        # Berechne Stop-Loss und Take-Profit
        if signal_type == SignalType.BUY:
            stop_loss = current_price * 0.95  # 5% Stop-Loss
            take_profit = current_price * 1.10  # 10% Take-Profit
        else:
            stop_loss = current_price * 1.05
            take_profit = current_price * 0.90
        
        return TradingSignal(
            symbol=symbol,
            timestamp=date,
            signal_type=signal_type,
            strength=strength,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=abs(signal_score),
            reasoning=f"Technical analysis score: {signal_score:.2f}",
            sentiment_score=0.0,  # Vereinfacht für Backtest
            technical_score=signal_score,
            volume_score=0.0,
            position_size_percent=2.0,  # 2% pro Position
            risk_reward_ratio=2.0
        )
    
    def _validate_signal(self, signal: TradingSignal, portfolio: Dict) -> bool:
        """Validiere Signal gegen Portfolio-Constraints"""
        
        # Prüfe verfügbares Kapital
        position_size = portfolio['portfolio_value'] * (signal.position_size_percent / 100)
        
        if position_size > portfolio['cash']:
            return False
        
        # Prüfe maximale Anzahl Positionen
        if len(portfolio['positions']) >= 5:  # Max 5 gleichzeitige Positionen
            return False
        
        return True
    
    def _open_position(self, signal: TradingSignal, portfolio: Dict, date: datetime):
        """Öffne neue Position"""
        
        # Berechne Position-Details
        position_size = portfolio['portfolio_value'] * (signal.position_size_percent / 100)
        
        # Berücksichtige Kommission und Slippage
        effective_price = signal.entry_price * (1 + self.slippage)
        commission_cost = position_size * self.commission
        
        quantity = (position_size - commission_cost) / effective_price
        
        # Erstelle Position
        position = {
            'symbol': signal.symbol,
            'signal_type': signal.signal_type,
            'entry_date': date,
            'entry_price': effective_price,
            'quantity': quantity,
            'position_value': quantity * effective_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'current_price': effective_price,
            'unrealized_pnl': 0.0,
            'commission_paid': commission_cost
        }
        
        # Update Portfolio
        portfolio['positions'][signal.symbol] = position
        portfolio['cash'] -= (position['position_value'] + commission_cost)
    
    def _close_position(self, symbol: str, portfolio: Dict, date: datetime, exit_reason: str):
        """Schließe Position"""
        
        position = portfolio['positions'][symbol]
        
        # Berechne Exit-Details
        exit_price = position['current_price']
        effective_exit_price = exit_price * (1 - self.slippage)
        
        exit_value = position['quantity'] * effective_exit_price
        commission_cost = exit_value * self.commission
        
        net_proceeds = exit_value - commission_cost
        
        # Berechne P&L
        total_cost = position['position_value'] + position['commission_paid'] + commission_cost
        pnl = net_proceeds - position['position_value']
        pnl_percent = (pnl / position['position_value']) * 100
        
        # Erstelle Trade-Record
        trade = BacktestTrade(
            symbol=symbol,
            entry_time=position['entry_date'],
            exit_time=date,
            signal_type=position['signal_type'],
            entry_price=position['entry_price'],
            exit_price=effective_exit_price,
            quantity=position['quantity'],
            pnl=pnl,
            pnl_percent=pnl_percent,
            duration_hours=(date - position['entry_date']).total_seconds() / 3600,
            exit_reason=exit_reason
        )
        
        # Update Portfolio
        portfolio['cash'] += net_proceeds
        portfolio['trades'].append(trade)
        del portfolio['positions'][symbol]
    
    def _check_exit_conditions(self, position: Dict, current_price: float, date: datetime) -> Tuple[bool, str]:
        """Prüfe Exit-Bedingungen für Position"""
        
        # Stop-Loss prüfen
        if position['signal_type'] == SignalType.BUY:
            if current_price <= position['stop_loss']:
                return True, "Stop-Loss"
            elif current_price >= position['take_profit']:
                return True, "Take-Profit"
        else:  # SELL
            if current_price >= position['stop_loss']:
                return True, "Stop-Loss"
            elif current_price <= position['take_profit']:
                return True, "Take-Profit"
        
        # Zeit-basierter Exit (max 30 Tage)
        days_open = (date - position['entry_date']).days
        if days_open > 30:
            return True, "Time-based Exit"
        
        return False, ""
    
    def _calculate_position_pnl(self, position: Dict, current_price: float) -> float:
        """Berechne unrealized P&L für Position"""
        
        if position['signal_type'] == SignalType.BUY:
            return (current_price - position['entry_price']) * position['quantity']
        else:
            return (position['entry_price'] - current_price) * position['quantity']
    
    def _calculate_backtest_metrics(self, portfolio: Dict, strategy_name: str, 
                                  start_date: datetime, end_date: datetime) -> BacktestResult:
        """Berechne umfassende Backtest-Metriken"""
        
        trades = portfolio['trades']
        daily_values = portfolio['daily_values']
        
        # Grundlegende Metriken
        final_capital = portfolio['portfolio_value']
        total_return = final_capital - self.initial_capital
        total_return_percent = (total_return / self.initial_capital) * 100
        
        # Trade-Statistiken
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        losing_trades = len([t for t in trades if t.pnl < 0])
        win_rate = (winning_trades / max(1, total_trades)) * 100
        
        # P&L-Statistiken
        if trades:
            wins = [t.pnl for t in trades if t.pnl > 0]
            losses = [t.pnl for t in trades if t.pnl < 0]
            
            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 0
            largest_win = max(wins) if wins else 0
            largest_loss = min(losses) if losses else 0
            
            profit_factor = abs(sum(wins) / sum(losses)) if losses else float('inf')
            avg_trade_duration = np.mean([t.duration_hours for t in trades])
        else:
            avg_win = avg_loss = largest_win = largest_loss = 0
            profit_factor = 0
            avg_trade_duration = 0
        
        # Risiko-Metriken
        if len(daily_values) > 1:
            values = [dv['value'] for dv in daily_values]
            returns = np.diff(values) / values[:-1]
            
            # Volatilität (annualisiert)
            volatility = np.std(returns) * np.sqrt(252) * 100
            
            # Max Drawdown
            peak = np.maximum.accumulate(values)
            drawdown = (values - peak) / peak
            max_drawdown = abs(np.min(drawdown)) * final_capital
            max_drawdown_percent = abs(np.min(drawdown)) * 100
            
            # Sharpe Ratio (vereinfacht, ohne Risk-free Rate)
            if volatility > 0:
                sharpe_ratio = (total_return_percent / volatility)
            else:
                sharpe_ratio = 0
            
            # Sortino Ratio
            negative_returns = returns[returns < 0]
            if len(negative_returns) > 0:
                downside_deviation = np.std(negative_returns) * np.sqrt(252) * 100
                sortino_ratio = total_return_percent / downside_deviation if downside_deviation > 0 else 0
            else:
                sortino_ratio = float('inf') if total_return_percent > 0 else 0
            
            # Calmar Ratio
            calmar_ratio = total_return_percent / max_drawdown_percent if max_drawdown_percent > 0 else 0
            
        else:
            volatility = max_drawdown = max_drawdown_percent = 0
            sharpe_ratio = sortino_ratio = calmar_ratio = 0
        
        return BacktestResult(
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            total_return_percent=total_return_percent,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            avg_trade_duration=avg_trade_duration,
            volatility=volatility,
            calmar_ratio=calmar_ratio
        )

def main():
    """Test des Backtesting-Frameworks"""
    print("=" * 80)
 print("BACKTESTING ENGINE TEST")
    print("=" * 80)
    
    engine = BacktestingEngine()
    
    # Test-Parameter
    symbols = ['BTC-USD', 'ETH-USD']
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # 30 Tage Backtest
    
    try:
        # Führe Backtest durch
        result = engine.run_backtest(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            strategy_name="Technical Analysis Strategy"
        )
        
        # Zeige Ergebnisse
 print(f"\n BACKTEST RESULTS:")
        print(f"   Strategy: {result.strategy_name}")
        print(f"   Period: {result.start_date.date()} to {result.end_date.date()}")
        print(f"   Initial Capital: ${result.initial_capital:,.2f}")
        print(f"   Final Capital: ${result.final_capital:,.2f}")
        print(f"   Total Return: ${result.total_return:+,.2f} ({result.total_return_percent:+.2f}%)")
        print(f"   Max Drawdown: ${result.max_drawdown:,.2f} ({result.max_drawdown_percent:.2f}%)")
        print(f"   Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"   Win Rate: {result.win_rate:.1f}%")
        print(f"   Total Trades: {result.total_trades}")
        print(f"   Profit Factor: {result.profit_factor:.2f}")
        print(f"   Volatility: {result.volatility:.2f}%")
        
        # Speichere Ergebnisse
        results_path = '/home/ubuntu/trading_system/backtest_results.json'
        with open(results_path, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
 print(f"\n Results saved to: {results_path}")
        
    except Exception as e:
 print(f" Backtest failed: {e}")
        print("This is expected if no historical data is available")

if __name__ == "__main__":
    main()

