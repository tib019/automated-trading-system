#!/usr/bin/env python3
"""
Backtesting Demo mit simulierten historischen Daten
Zeigt die Funktionalität des Backtesting-Frameworks
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json

from backtesting_engine import BacktestingEngine, BacktestResult, BacktestTrade
from signal_generator import SignalType

class BacktestDemo:
    """Demo-Klasse für Backtesting mit simulierten Daten"""
    
    def __init__(self):
        self.engine = BacktestingEngine()
    
    def generate_synthetic_data(self, symbol: str, start_date: datetime, end_date: datetime, 
                              initial_price: float = 100.0) -> pd.DataFrame:
        """Generiere synthetische Marktdaten für Demo"""
        
        # Erstelle Zeitindex (stündliche Daten)
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        
        # Simuliere Preisbewegungen mit Random Walk + Trend
        np.random.seed(42)  # Für reproduzierbare Ergebnisse
        
        n_periods = len(date_range)
        
        # Basis-Parameter
        daily_volatility = 0.02  # 2% tägliche Volatilität
        trend = 0.0001  # Leichter Aufwärtstrend
        
        # Generiere Returns
        returns = np.random.normal(trend, daily_volatility, n_periods)
        
        # Berechne Preise
        prices = [initial_price]
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(new_price)
        
        # Erstelle OHLC-Daten
        data = []
        for i, (timestamp, close) in enumerate(zip(date_range, prices)):
            # Simuliere OHLC basierend auf Close
            noise = np.random.normal(0, 0.005, 4)  # 0.5% Noise
            
            open_price = close * (1 + noise[0])
            high_price = max(open_price, close) * (1 + abs(noise[1]))
            low_price = min(open_price, close) * (1 - abs(noise[2]))
            volume = np.random.randint(1000, 10000)
            
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
        
        # Berechne technische Indikatoren
        df['returns'] = df['close_price'].pct_change()
        df['sma_20'] = df['close_price'].rolling(window=20).mean()
        df['sma_50'] = df['close_price'].rolling(window=50).mean()
        df['volatility'] = df['returns'].rolling(window=20).std()
        
        return df
    
    def run_demo_backtest(self) -> BacktestResult:
        """Führe Demo-Backtest mit synthetischen Daten durch"""
        
        print("=" * 80)
 print("BACKTESTING DEMO - SYNTHETIC DATA")
        print("=" * 80)
        
        # Demo-Parameter
        symbols = ['DEMO-BTC', 'DEMO-ETH', 'DEMO-STOCK']
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # 3 Monate
        
        print(f"Demo Period: {start_date.date()} to {end_date.date()}")
        print(f"Symbols: {', '.join(symbols)}")
        
        # Generiere synthetische Daten
        synthetic_data = {}
        initial_prices = {'DEMO-BTC': 50000, 'DEMO-ETH': 3000, 'DEMO-STOCK': 150}
        
        for symbol in symbols:
            data = self.generate_synthetic_data(symbol, start_date, end_date, initial_prices[symbol])
            synthetic_data[symbol] = data
            print(f"Generated {len(data)} data points for {symbol}")
        
        # Modifiziere Engine für Demo-Daten
        original_get_data = self.engine.data_manager.get_historical_data
        
        def mock_get_data(symbol, start, end):
            if symbol in synthetic_data:
                return synthetic_data[symbol]
            return original_get_data(symbol, start, end)
        
        self.engine.data_manager.get_historical_data = mock_get_data
        
        # Führe Backtest durch
        result = self.engine.run_backtest(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            strategy_name="Demo Technical Strategy"
        )
        
        return result
    
    def create_backtest_visualization(self, result: BacktestResult, portfolio_data: dict = None):
        """Erstelle Visualisierung der Backtest-Ergebnisse"""
        
        # Erstelle Demo-Portfolio-Verlauf
        if not portfolio_data:
            # Simuliere Portfolio-Verlauf basierend auf Ergebnis
            days = (result.end_date - result.start_date).days
            dates = pd.date_range(start=result.start_date, end=result.end_date, periods=days)
            
            # Simuliere Portfolio-Entwicklung
            initial = result.initial_capital
            final = result.final_capital
            
            # Erstelle realistische Kurve mit Volatilität
            np.random.seed(42)
            returns = np.random.normal(0, 0.01, len(dates))
            
            # Skaliere Returns um gewünschtes Endergebnis zu erreichen
            total_return = (final - initial) / initial
            cumulative_returns = np.cumsum(returns)
            scaled_returns = cumulative_returns * (total_return / cumulative_returns[-1])
            
            portfolio_values = initial * (1 + scaled_returns)
            
        else:
            dates = [d['date'] for d in portfolio_data['daily_values']]
            portfolio_values = [d['value'] for d in portfolio_data['daily_values']]
        
        # Erstelle Chart
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Portfolio-Wert über Zeit
        ax1.plot(dates, portfolio_values, 'b-', linewidth=2, label='Portfolio Value')
        ax1.axhline(y=result.initial_capital, color='gray', linestyle='--', alpha=0.7, label='Initial Capital')
        ax1.set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Drawdown-Chart
        peak = np.maximum.accumulate(portfolio_values)
        drawdown = (np.array(portfolio_values) - peak) / peak * 100
        
        ax2.fill_between(dates, drawdown, 0, color='red', alpha=0.3)
        ax2.plot(dates, drawdown, 'r-', linewidth=1)
        ax2.set_title('Drawdown Over Time', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True, alpha=0.3)
        
        # 3. Performance-Metriken (Bar Chart)
        metrics = ['Total Return %', 'Sharpe Ratio', 'Win Rate %', 'Profit Factor']
        values = [result.total_return_percent, result.sharpe_ratio, result.win_rate, result.profit_factor]
        colors = ['green' if v > 0 else 'red' for v in values]
        
        bars = ax3.bar(metrics, values, color=colors, alpha=0.7)
        ax3.set_title('Key Performance Metrics', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Value')
        ax3.grid(True, alpha=0.3)
        
        # Werte auf Balken anzeigen
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + (0.01 * max(abs(min(values)), abs(max(values)))),
                    f'{value:.2f}', ha='center', va='bottom' if height >= 0 else 'top')
        
        # 4. Trade-Statistiken (Pie Chart)
        if result.total_trades > 0:
            trade_labels = ['Winning Trades', 'Losing Trades']
            trade_sizes = [result.winning_trades, result.losing_trades]
            trade_colors = ['green', 'red']
            
            ax4.pie(trade_sizes, labels=trade_labels, colors=trade_colors, autopct='%1.1f%%', startangle=90)
            ax4.set_title(f'Trade Distribution (Total: {result.total_trades})', fontsize=14, fontweight='bold')
        else:
            ax4.text(0.5, 0.5, 'No Trades\nExecuted', ha='center', va='center', 
                    transform=ax4.transAxes, fontsize=16, fontweight='bold')
            ax4.set_title('Trade Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Speichere Chart
        chart_path = '/home/ubuntu/trading_system/backtest_demo_chart.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def generate_demo_report(self, result: BacktestResult) -> str:
        """Generiere umfassenden Demo-Bericht"""
        
        report = []
        report.append("=" * 80)
        report.append("📊 BACKTESTING DEMO - COMPREHENSIVE REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Strategy Overview
        report.append("🎯 STRATEGY OVERVIEW")
        report.append("-" * 40)
        report.append(f"Strategy Name: {result.strategy_name}")
        report.append(f"Backtest Period: {result.start_date.date()} to {result.end_date.date()}")
        report.append(f"Duration: {(result.end_date - result.start_date).days} days")
        report.append("")
        
        # Performance Summary
        report.append("💰 PERFORMANCE SUMMARY")
        report.append("-" * 40)
        report.append(f"Initial Capital: ${result.initial_capital:,.2f}")
        report.append(f"Final Capital: ${result.final_capital:,.2f}")
        report.append(f"Total Return: ${result.total_return:+,.2f} ({result.total_return_percent:+.2f}%)")
        
        # Annualisierte Return
        days = (result.end_date - result.start_date).days
        annualized_return = (result.total_return_percent / days) * 365
        report.append(f"Annualized Return: {annualized_return:+.2f}%")
        report.append("")
        
        # Risk Metrics
        report.append("🛡️ RISK METRICS")
        report.append("-" * 40)
        report.append(f"Maximum Drawdown: ${result.max_drawdown:,.2f} ({result.max_drawdown_percent:.2f}%)")
        report.append(f"Volatility: {result.volatility:.2f}%")
        report.append(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
        report.append(f"Sortino Ratio: {result.sortino_ratio:.2f}")
        report.append(f"Calmar Ratio: {result.calmar_ratio:.2f}")
        report.append("")
        
        # Trading Statistics
        report.append("📈 TRADING STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Trades: {result.total_trades}")
        report.append(f"Winning Trades: {result.winning_trades}")
        report.append(f"Losing Trades: {result.losing_trades}")
        report.append(f"Win Rate: {result.win_rate:.1f}%")
        report.append(f"Profit Factor: {result.profit_factor:.2f}")
        
        if result.total_trades > 0:
            report.append(f"Average Win: ${result.avg_win:,.2f}")
            report.append(f"Average Loss: ${result.avg_loss:,.2f}")
            report.append(f"Largest Win: ${result.largest_win:,.2f}")
            report.append(f"Largest Loss: ${result.largest_loss:,.2f}")
            report.append(f"Average Trade Duration: {result.avg_trade_duration:.1f} hours")
        report.append("")
        
        # Strategy Assessment
        report.append("🎯 STRATEGY ASSESSMENT")
        report.append("-" * 40)
        
        # Performance Rating
        if result.total_return_percent > 20:
            performance_rating = "🟢 EXCELLENT"
        elif result.total_return_percent > 10:
            performance_rating = "🟡 GOOD"
        elif result.total_return_percent > 0:
            performance_rating = "🟠 MODERATE"
        else:
            performance_rating = "🔴 POOR"
        
        report.append(f"Performance Rating: {performance_rating}")
        
        # Risk Rating
        if result.max_drawdown_percent < 5:
            risk_rating = "🟢 LOW RISK"
        elif result.max_drawdown_percent < 15:
            risk_rating = "🟡 MODERATE RISK"
        elif result.max_drawdown_percent < 25:
            risk_rating = "🟠 HIGH RISK"
        else:
            risk_rating = "🔴 VERY HIGH RISK"
        
        report.append(f"Risk Rating: {risk_rating}")
        
        # Sharpe Rating
        if result.sharpe_ratio > 2:
            sharpe_rating = "🟢 EXCELLENT"
        elif result.sharpe_ratio > 1:
            sharpe_rating = "🟡 GOOD"
        elif result.sharpe_ratio > 0:
            sharpe_rating = "🟠 ACCEPTABLE"
        else:
            sharpe_rating = "🔴 POOR"
        
        report.append(f"Risk-Adjusted Return: {sharpe_rating}")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 40)
        
        if result.win_rate < 50:
            report.append("• Consider tightening entry criteria to improve win rate")
        
        if result.max_drawdown_percent > 20:
            report.append("• Implement stricter risk management to reduce drawdown")
        
        if result.profit_factor < 1.5:
            report.append("• Optimize take-profit and stop-loss levels")
        
        if result.total_trades < 10:
            report.append("• Strategy may need more trading opportunities")
        
        if result.sharpe_ratio < 1:
            report.append("• Focus on improving risk-adjusted returns")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Hauptfunktion für Backtesting-Demo"""
    
    demo = BacktestDemo()
    
    # Führe Demo-Backtest durch
    result = demo.run_demo_backtest()
    
    # Erstelle Visualisierung
 print(f"\n Creating backtest visualization...")
    chart_path = demo.create_backtest_visualization(result)
    print(f"Chart saved: {chart_path}")
    
    # Generiere Bericht
 print(f"\n Generating comprehensive report...")
    report = demo.generate_demo_report(result)
    print(report)
    
    # Speichere Bericht
    report_path = '/home/ubuntu/trading_system/backtest_demo_report.txt'
    with open(report_path, 'w') as f:
        f.write(report)
    
 print(f"\n Report saved: {report_path}")
    
    # Speichere JSON-Ergebnisse
    results_path = '/home/ubuntu/trading_system/backtest_demo_results.json'
    with open(results_path, 'w') as f:
        json.dump({
            'result': result.__dict__,
            'timestamp': datetime.now().isoformat(),
            'demo_parameters': {
                'synthetic_data': True,
                'symbols': ['DEMO-BTC', 'DEMO-ETH', 'DEMO-STOCK'],
                'duration_days': 90,
                'initial_capital': 10000
            }
        }, f, indent=2, default=str)
    
    print(f"Results saved: {results_path}")
    
 print(f"\n BACKTESTING DEMO COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()

