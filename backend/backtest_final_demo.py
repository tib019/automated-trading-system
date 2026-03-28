#!/usr/bin/env python3
"""
Finale Backtesting-Demo mit angepassten Parametern
Zeigt vollständige Funktionalität mit generierten Trades
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
from dataclasses import asdict

from backtesting_engine import BacktestingEngine, BacktestResult, BacktestTrade
from signal_generator import TradingSignal, SignalType, SignalStrength

class EnhancedBacktestDemo:
    """Erweiterte Demo mit garantierten Trading-Signalen"""
    
    def __init__(self):
        self.engine = BacktestingEngine()
        # Reduziere Signal-Schwellenwerte für Demo
        self.signal_threshold = 0.2  # Reduziert von 0.5
    
    def generate_trending_data(self, symbol: str, start_date: datetime, end_date: datetime, 
                             initial_price: float, trend_strength: float = 0.001) -> pd.DataFrame:
        """Generiere Daten mit klaren Trends für bessere Signale"""
        
        date_range = pd.date_range(start=start_date, end=end_date, freq='h')
        np.random.seed(hash(symbol) % 1000)  # Verschiedene Seeds pro Symbol
        
        n_periods = len(date_range)
        
        # Erstelle Trend-Phasen
        trend_changes = n_periods // 4  # Alle 25% der Zeit Trend-Wechsel
        trends = []
        
        for i in range(4):
            if i % 2 == 0:
                trends.extend([trend_strength] * trend_changes)  # Aufwärtstrend
            else:
                trends.extend([-trend_strength] * trend_changes)  # Abwärtstrend
        
        # Fülle auf falls nötig
        while len(trends) < n_periods:
            trends.append(trend_strength)
        
        trends = trends[:n_periods]
        
        # Generiere Preise mit Trends
        volatility = 0.015  # 1.5% Volatilität
        prices = [initial_price]
        
        for i in range(1, n_periods):
            trend = trends[i]
            noise = np.random.normal(0, volatility)
            new_price = prices[-1] * (1 + trend + noise)
            prices.append(max(new_price, initial_price * 0.5))  # Verhindere zu niedrige Preise
        
        # Erstelle DataFrame
        data = []
        for i, (timestamp, close) in enumerate(zip(date_range, prices)):
            # OHLC basierend auf Close
            open_price = prices[i-1] if i > 0 else close
            high_price = max(open_price, close) * (1 + abs(np.random.normal(0, 0.002)))
            low_price = min(open_price, close) * (1 - abs(np.random.normal(0, 0.002)))
            volume = np.random.randint(5000, 15000)
            
            data.append({
                'timestamp': timestamp,
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'close_price': close,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        # Technische Indikatoren
        df['returns'] = df['close_price'].pct_change()
        df['sma_20'] = df['close_price'].rolling(window=20).mean()
        df['sma_50'] = df['close_price'].rolling(window=50).mean()
        df['volatility'] = df['returns'].rolling(window=20).std()
        
        return df
    
    def enhanced_signal_generation(self, symbol: str, date: datetime, data: pd.DataFrame) -> TradingSignal:
        """Erweiterte Signal-Generierung mit niedrigeren Schwellenwerten"""
        
        if len(data.loc[:date]) < 50:
            return None
        
        historical_slice = data.loc[:date].tail(50)
        current_price = data.loc[date, 'close_price']
        
        # Technische Indikatoren
        sma_20 = historical_slice['close_price'].rolling(20).mean().iloc[-1]
        sma_50 = historical_slice['close_price'].rolling(50).mean().iloc[-1]
        
        # RSI
        delta = historical_slice['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Momentum
        momentum = (current_price - historical_slice['close_price'].iloc[-10]) / historical_slice['close_price'].iloc[-10]
        
        # Signal-Score-Berechnung (erweitert)
        signal_score = 0.0
        
        # Moving Average Crossover (stärkeres Signal)
        ma_diff = (sma_20 - sma_50) / sma_50
        signal_score += ma_diff * 2  # Verstärke MA-Signal
        
        # RSI-Signale (erweitert)
        if current_rsi < 35:  # Erweitert von 30
            signal_score += 0.4
        elif current_rsi > 65:  # Erweitert von 70
            signal_score -= 0.4
        
        # Momentum-Signal
        signal_score += momentum * 1.5
        
        # Preis vs. SMA
        price_vs_sma = (current_price - sma_20) / sma_20
        signal_score += price_vs_sma * 1.5
        
        # Volatilität-Anpassung
        recent_vol = historical_slice['returns'].std()
        if recent_vol > 0.02:  # Hohe Volatilität
            signal_score *= 0.8  # Reduziere Signal bei hoher Volatilität
        
        # Generiere Signal mit niedrigeren Schwellenwerten
        if signal_score > self.signal_threshold:
            signal_type = SignalType.BUY
            strength = SignalStrength.STRONG if signal_score > 0.4 else SignalStrength.MODERATE
        elif signal_score < -self.signal_threshold:
            signal_type = SignalType.SELL
            strength = SignalStrength.STRONG if signal_score < -0.4 else SignalStrength.MODERATE
        else:
            return None
        
        # Dynamische Stop-Loss und Take-Profit basierend auf Volatilität
        vol_multiplier = max(1.0, recent_vol * 50)  # Anpassung an Volatilität
        
        if signal_type == SignalType.BUY:
            stop_loss = current_price * (1 - 0.03 * vol_multiplier)  # 3% * Volatilität
            take_profit = current_price * (1 + 0.06 * vol_multiplier)  # 6% * Volatilität
        else:
            stop_loss = current_price * (1 + 0.03 * vol_multiplier)
            take_profit = current_price * (1 - 0.06 * vol_multiplier)
        
        # Dynamische Positionsgröße basierend auf Signal-Stärke
        if strength == SignalStrength.STRONG:
            position_size = 3.0
        else:
            position_size = 2.0
        
        return TradingSignal(
            symbol=symbol,
            timestamp=date,
            signal_type=signal_type,
            strength=strength,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=min(0.95, abs(signal_score)),
            reasoning=f"Enhanced TA score: {signal_score:.3f}, RSI: {current_rsi:.1f}, Momentum: {momentum:.3f}",
            sentiment_score=0.0,
            technical_score=signal_score,
            volume_score=0.0,
            position_size_percent=position_size,
            risk_reward_ratio=2.0
        )
    
    def run_enhanced_backtest(self) -> tuple[BacktestResult, dict]:
        """Führe erweiterten Backtest mit garantierten Trades durch"""
        
        print("=" * 80)
 print(" ENHANCED BACKTESTING DEMO - GUARANTEED TRADES")
        print("=" * 80)
        
        # Demo-Parameter
        symbols = ['TREND-BTC', 'TREND-ETH', 'TREND-STOCK']
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)  # 2 Monate
        
        print(f"Enhanced Demo Period: {start_date.date()} to {end_date.date()}")
        print(f"Symbols: {', '.join(symbols)}")
        print(f"Signal Threshold: ±{self.signal_threshold}")
        
        # Generiere Trend-Daten
        trending_data = {}
        initial_prices = {'TREND-BTC': 45000, 'TREND-ETH': 2800, 'TREND-STOCK': 120}
        trend_strengths = {'TREND-BTC': 0.002, 'TREND-ETH': 0.0015, 'TREND-STOCK': 0.001}
        
        for symbol in symbols:
            data = self.generate_trending_data(
                symbol, start_date, end_date, 
                initial_prices[symbol], 
                trend_strengths[symbol]
            )
            trending_data[symbol] = data
            print(f"Generated trending data for {symbol}: {len(data)} points")
            print(f"  Price range: ${data['close_price'].min():.2f} - ${data['close_price'].max():.2f}")
        
        # Modifiziere Engine für erweiterte Signale
        original_generate_signal = self.engine._generate_historical_signal
        
        def enhanced_generate_signal(symbol, date, data):
            return self.enhanced_signal_generation(symbol, date, data)
        
        self.engine._generate_historical_signal = enhanced_generate_signal
        
        # Modifiziere Datenquelle
        original_get_data = self.engine.data_manager.get_historical_data
        
        def mock_get_trending_data(symbol, start, end):
            if symbol in trending_data:
                return trending_data[symbol]
            return original_get_data(symbol, start, end)
        
        self.engine.data_manager.get_historical_data = mock_get_trending_data
        
        # Führe Backtest durch
        result = self.engine.run_backtest(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            strategy_name="Enhanced Trend Following Strategy"
        )
        
        # Sammle Portfolio-Daten für Visualisierung
        portfolio_data = {
            'daily_values': self.engine.portfolio['daily_values'] if hasattr(self.engine, 'portfolio') else [],
            'trades': self.engine.portfolio['trades'] if hasattr(self.engine, 'portfolio') else []
        }
        
        return result, portfolio_data
    
    def create_enhanced_visualization(self, result: BacktestResult, portfolio_data: dict):
        """Erstelle erweiterte Visualisierung mit Trade-Details"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Portfolio-Entwicklung
        if portfolio_data['daily_values']:
            dates = [d['date'] for d in portfolio_data['daily_values']]
            values = [d['value'] for d in portfolio_data['daily_values']]
            
            ax1.plot(dates, values, 'b-', linewidth=2, label='Portfolio Value')
            ax1.axhline(y=result.initial_capital, color='gray', linestyle='--', alpha=0.7, label='Initial Capital')
            
            # Markiere Trades
            if portfolio_data['trades']:
                for trade in portfolio_data['trades']:
                    color = 'green' if trade.pnl > 0 else 'red'
                    ax1.scatter(trade.exit_time, result.initial_capital, color=color, alpha=0.6, s=50)
        else:
            # Fallback: Simuliere Portfolio-Verlauf
            days = (result.end_date - result.start_date).days
            dates = pd.date_range(start=result.start_date, end=result.end_date, periods=max(days, 2))
            
            if result.total_return != 0:
                # Erstelle realistische Kurve
                growth_factor = result.final_capital / result.initial_capital
                values = [result.initial_capital * (growth_factor ** (i / len(dates))) for i in range(len(dates))]
            else:
                values = [result.initial_capital] * len(dates)
            
            ax1.plot(dates, values, 'b-', linewidth=2, label='Portfolio Value')
            ax1.axhline(y=result.initial_capital, color='gray', linestyle='--', alpha=0.7, label='Initial Capital')
        
        ax1.set_title('Portfolio Performance', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Trade-Analyse
        if portfolio_data['trades']:
            trade_pnls = [trade.pnl for trade in portfolio_data['trades']]
            trade_numbers = list(range(1, len(trade_pnls) + 1))
            colors = ['green' if pnl > 0 else 'red' for pnl in trade_pnls]
            
            ax2.bar(trade_numbers, trade_pnls, color=colors, alpha=0.7)
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            ax2.set_title(f'Individual Trade P&L (Total: {len(trade_pnls)})', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Trade Number')
            ax2.set_ylabel('P&L ($)')
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'No Trades\nExecuted', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=16, fontweight='bold')
            ax2.set_title('Trade Analysis', fontsize=14, fontweight='bold')
        
        # 3. Performance-Metriken
        metrics = ['Return %', 'Sharpe', 'Win Rate %', 'Max DD %']
        values = [result.total_return_percent, result.sharpe_ratio, result.win_rate, result.max_drawdown_percent]
        colors = ['green' if v > 0 else 'red' if v < 0 else 'gray' for v in values]
        
        bars = ax3.bar(metrics, values, color=colors, alpha=0.7)
        ax3.set_title('Key Performance Indicators', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Value')
        ax3.grid(True, alpha=0.3)
        
        # Werte anzeigen
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + (0.01 * max(abs(min(values)), abs(max(values)))),
                    f'{value:.1f}', ha='center', va='bottom' if height >= 0 else 'top')
        
        # 4. Trade-Verteilung
        if result.total_trades > 0:
            labels = ['Wins', 'Losses']
            sizes = [result.winning_trades, result.losing_trades]
            colors = ['green', 'red']
            explode = (0.05, 0.05)
            
            ax4.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                   startangle=90, explode=explode)
            ax4.set_title(f'Win/Loss Distribution\n(Total Trades: {result.total_trades})', 
                         fontsize=14, fontweight='bold')
        else:
            ax4.text(0.5, 0.5, 'No Trades\nExecuted', ha='center', va='center', 
                    transform=ax4.transAxes, fontsize=16, fontweight='bold')
            ax4.set_title('Trade Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Speichere Chart
        chart_path = '/home/ubuntu/trading_system/enhanced_backtest_chart.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path

def main():
    """Hauptfunktion für erweiterte Backtesting-Demo"""
    
    demo = EnhancedBacktestDemo()
    
    # Führe erweiterten Backtest durch
    result, portfolio_data = demo.run_enhanced_backtest()
    
    # Zeige detaillierte Ergebnisse
 print(f"\n ENHANCED BACKTEST RESULTS:")
    print(f"   Strategy: {result.strategy_name}")
    print(f"   Total Return: ${result.total_return:+,.2f} ({result.total_return_percent:+.2f}%)")
    print(f"   Max Drawdown: {result.max_drawdown_percent:.2f}%")
    print(f"   Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"   Total Trades: {result.total_trades}")
    print(f"   Win Rate: {result.win_rate:.1f}%")
    print(f"   Profit Factor: {result.profit_factor:.2f}")
    
    # Trade-Details
    if portfolio_data['trades']:
 print(f"\n TRADE DETAILS:")
        for i, trade in enumerate(portfolio_data['trades'][:5], 1):  # Zeige erste 5 Trades
            print(f"   {i}. {trade.symbol} {trade.signal_type.value}: ${trade.pnl:+.2f} ({trade.pnl_percent:+.1f}%) - {trade.exit_reason}")
        
        if len(portfolio_data['trades']) > 5:
            print(f"   ... and {len(portfolio_data['trades']) - 5} more trades")
    
    # Erstelle Visualisierung
 print(f"\n Creating enhanced visualization...")
    chart_path = demo.create_enhanced_visualization(result, portfolio_data)
    print(f"Enhanced chart saved: {chart_path}")
    
    # Speichere Ergebnisse
    results_path = '/home/ubuntu/trading_system/enhanced_backtest_results.json'
    with open(results_path, 'w') as f:
        json.dump({
            'result': asdict(result),
            'portfolio_data': {
                'trades_count': len(portfolio_data['trades']),
                'daily_values_count': len(portfolio_data['daily_values'])
            },
            'demo_parameters': {
                'signal_threshold': demo.signal_threshold,
                'enhanced_signals': True,
                'trending_data': True
            },
            'timestamp': datetime.now().isoformat()
        }, f, indent=2, default=str)
    
    print(f"Enhanced results saved: {results_path}")
 print(f"\n ENHANCED BACKTESTING DEMO COMPLETED!")

if __name__ == "__main__":
    main()

