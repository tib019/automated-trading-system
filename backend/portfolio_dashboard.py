#!/usr/bin/env python3
"""
Trading System - Portfolio Dashboard
Interaktives Dashboard für Portfolio-Monitoring und Risikomanagement
"""

import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import List, Dict
import json

from risk_manager import RiskManager, PortfolioTracker, Position, PositionStatus
from config import get_config

class PortfolioDashboard:
    """Portfolio-Dashboard für Visualisierung und Monitoring"""
    
    def __init__(self):
        self.config = get_config()
        self.risk_manager = RiskManager()
        self.portfolio_tracker = self.risk_manager.portfolio_tracker
        
        # Matplotlib-Konfiguration
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def generate_portfolio_report(self) -> str:
        """Generiere umfassenden Portfolio-Bericht"""
        monitoring_result = self.risk_manager.monitor_portfolio()
        metrics = monitoring_result['portfolio_metrics']
        
        report = []
        report.append("=" * 80)
        report.append("📊 TRADING SYSTEM - PORTFOLIO REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Portfolio-Übersicht
        report.append("💼 PORTFOLIO OVERVIEW")
        report.append("-" * 40)
        report.append(f"Total Portfolio Value: ${metrics['total_value']:,.2f}")
        report.append(f"Initial Capital: ${self.config.BACKTESTING['initial_capital']:,.2f}")
        report.append(f"Cash Balance: ${metrics['cash_balance']:,.2f}")
        report.append(f"Invested Amount: ${metrics['invested_amount']:,.2f}")
        report.append(f"Total P&L: ${metrics['total_pnl']:+,.2f} ({(metrics['total_pnl']/self.config.BACKTESTING['initial_capital']*100):+.2f}%)")
        report.append(f"Daily P&L: ${metrics['daily_pnl']:+,.2f}")
        report.append("")
        
        # Risiko-Metriken
        risk_emoji = {
            'LOW': '🟢',
            'MODERATE': '🟡', 
            'HIGH': '🟠',
            'CRITICAL': '🔴'
        }
        
        report.append("🛡️ RISK METRICS")
        report.append("-" * 40)
        report.append(f"Risk Level: {risk_emoji.get(metrics['risk_level'], '⚪')} {metrics['risk_level']}")
        report.append(f"Open Positions: {metrics['open_positions']}")
        report.append(f"Total Positions: {metrics['total_positions']}")
        report.append(f"Win Rate: {metrics['win_rate']:.1f}%")
        report.append(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
        report.append(f"Portfolio Exposure: {(metrics['invested_amount']/metrics['total_value']*100):.1f}%")
        report.append("")
        
        # Offene Positionen
        open_positions = self.portfolio_tracker.get_open_positions()
        if open_positions:
            report.append("📈 OPEN POSITIONS")
            report.append("-" * 40)
            
            for pos in open_positions:
                pnl_percent = (pos.unrealized_pnl / pos.position_size_usd) * 100
                direction = "🟢 LONG" if pos.signal_type.value == "BUY" else "🔴 SHORT"
                status_emoji = "📈" if pos.unrealized_pnl > 0 else "📉" if pos.unrealized_pnl < 0 else "➡️"
                
                report.append(f"{direction} {pos.symbol}")
                report.append(f"  Entry: ${pos.entry_price:,.2f} | Current: ${pos.current_price:,.2f}")
                report.append(f"  Size: ${pos.position_size_usd:,.2f} | Qty: {pos.quantity:.6f}")
                report.append(f"  P&L: {status_emoji} ${pos.unrealized_pnl:+,.2f} ({pnl_percent:+.1f}%)")
                report.append(f"  Stop Loss: ${pos.stop_loss:,.2f} | Take Profit: ${pos.take_profit:,.2f}")
                report.append("")
        else:
            report.append("📈 OPEN POSITIONS")
            report.append("-" * 40)
            report.append("No open positions")
            report.append("")
        
        # Alerts und Aktionen
        if monitoring_result['alerts']:
            report.append("⚠️ ALERTS")
            report.append("-" * 40)
            for alert in monitoring_result['alerts']:
                report.append(f"• {alert}")
            report.append("")
        
        if monitoring_result['actions_taken']:
            report.append("🚨 ACTIONS TAKEN")
            report.append("-" * 40)
            for action in monitoring_result['actions_taken']:
                report.append(f"• {action}")
            report.append("")
        
        # Kill-Switch Status
        kill_switch_emoji = "🔴 ACTIVE" if monitoring_result['kill_switch_active'] else "🟢 INACTIVE"
        report.append("🛑 KILL-SWITCH STATUS")
        report.append("-" * 40)
        report.append(f"Status: {kill_switch_emoji}")
        report.append("")
        
        # Jüngste Risiko-Events
        risk_events = self._get_recent_risk_events(5)
        if risk_events:
            report.append("📋 RECENT RISK EVENTS")
            report.append("-" * 40)
            for event in risk_events:
                timestamp = event[1][:19] if isinstance(event[1], str) else str(event[1])[:19]
                report.append(f"{timestamp} | {event[3]} | {event[2]}")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def create_portfolio_chart(self, days: int = 7) -> str:
        """Erstelle Portfolio-Performance-Chart"""
        # Hole Portfolio-Historie
        history = self._get_portfolio_history(days)
        
        if len(history) < 2:
            return "Nicht genügend Daten für Chart-Erstellung"
        
        # Daten vorbereiten
        timestamps = [datetime.fromisoformat(row[1]) if isinstance(row[1], str) else row[1] for row in history]
        total_values = [row[2] for row in history]
        pnl_values = [row[5] for row in history]
        
        # Chart erstellen
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Portfolio Value Chart
        ax1.plot(timestamps, total_values, 'b-', linewidth=2, label='Portfolio Value')
        ax1.axhline(y=self.config.BACKTESTING['initial_capital'], color='gray', linestyle='--', alpha=0.7, label='Initial Capital')
        ax1.set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Format x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        
        # P&L Chart
        colors = ['green' if pnl >= 0 else 'red' for pnl in pnl_values]
        ax2.bar(timestamps, pnl_values, color=colors, alpha=0.7, label='Total P&L')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.set_title('Profit & Loss Over Time', fontsize=14, fontweight='bold')
        ax2.set_ylabel('P&L ($)')
        ax2.set_xlabel('Time')
        ax2.grid(True, alpha=0.3)
        
        # Format x-axis
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        ax2.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        
        # Rotate x-axis labels
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Speichere Chart
        chart_path = '/home/ubuntu/trading_system/portfolio_chart.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def create_positions_chart(self) -> str:
        """Erstelle Chart für offene Positionen"""
        open_positions = self.portfolio_tracker.get_open_positions()
        
        if not open_positions:
            return "Keine offenen Positionen für Chart"
        
        # Daten vorbereiten
        symbols = [pos.symbol for pos in open_positions]
        pnl_values = [pos.unrealized_pnl for pos in open_positions]
        pnl_percentages = [(pos.unrealized_pnl / pos.position_size_usd) * 100 for pos in open_positions]
        
        # Chart erstellen
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # P&L in Dollar
        colors = ['green' if pnl >= 0 else 'red' for pnl in pnl_values]
        bars1 = ax1.bar(symbols, pnl_values, color=colors, alpha=0.7)
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax1.set_title('Unrealized P&L by Position ($)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('P&L ($)')
        ax1.grid(True, alpha=0.3)
        
        # Werte auf Balken anzeigen
        for bar, pnl in zip(bars1, pnl_values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + (0.01 * max(abs(min(pnl_values)), abs(max(pnl_values)))),
                    f'${pnl:.2f}', ha='center', va='bottom' if height >= 0 else 'top')
        
        # P&L in Prozent
        colors = ['green' if pnl >= 0 else 'red' for pnl in pnl_percentages]
        bars2 = ax2.bar(symbols, pnl_percentages, color=colors, alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.set_title('Unrealized P&L by Position (%)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('P&L (%)')
        ax2.grid(True, alpha=0.3)
        
        # Werte auf Balken anzeigen
        for bar, pnl in zip(bars2, pnl_percentages):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + (0.01 * max(abs(min(pnl_percentages)), abs(max(pnl_percentages)))),
                    f'{pnl:.1f}%', ha='center', va='bottom' if height >= 0 else 'top')
        
        plt.tight_layout()
        
        # Speichere Chart
        chart_path = '/home/ubuntu/trading_system/positions_chart.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def export_portfolio_data(self) -> str:
        """Exportiere Portfolio-Daten als JSON"""
        monitoring_result = self.risk_manager.monitor_portfolio()
        open_positions = self.portfolio_tracker.get_open_positions()
        
        # Fix RiskLevel serialization
        portfolio_metrics = monitoring_result['portfolio_metrics'].copy()
        portfolio_metrics['risk_level'] = portfolio_metrics['risk_level'].value if hasattr(portfolio_metrics['risk_level'], 'value') else str(portfolio_metrics['risk_level'])
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_metrics': portfolio_metrics,
            'alerts': monitoring_result['alerts'],
            'actions_taken': monitoring_result['actions_taken'],
            'kill_switch_active': monitoring_result['kill_switch_active'],
            'open_positions': [
                {
                    'id': pos.id,
                    'symbol': pos.symbol,
                    'signal_type': pos.signal_type.value,
                    'entry_price': pos.entry_price,
                    'current_price': pos.current_price,
                    'quantity': pos.quantity,
                    'position_size_usd': pos.position_size_usd,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'pnl_percentage': (pos.unrealized_pnl / pos.position_size_usd) * 100,
                    'stop_loss': pos.stop_loss,
                    'take_profit': pos.take_profit,
                    'entry_time': pos.entry_time.isoformat(),
                    'status': pos.status.value
                }
                for pos in open_positions
            ]
        }
        
        export_path = '/home/ubuntu/trading_system/portfolio_export.json'
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return export_path
    
    def _get_portfolio_history(self, days: int) -> List:
        """Hole Portfolio-Historie der letzten N Tage"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.portfolio_tracker.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM portfolio_history 
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            ''', (cutoff_time,))
            
            return cursor.fetchall()
    
    def _get_recent_risk_events(self, limit: int = 10) -> List:
        """Hole jüngste Risiko-Events"""
        with sqlite3.connect(self.portfolio_tracker.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM risk_events 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return cursor.fetchall()

def main():
    """Test des Portfolio-Dashboards"""
    print("=" * 80)
 print("PORTFOLIO DASHBOARD TEST")
    print("=" * 80)
    
    dashboard = PortfolioDashboard()
    
    # Generiere Portfolio-Bericht
    report = dashboard.generate_portfolio_report()
    print(report)
    
    # Erstelle Charts
 print("\n Creating portfolio charts...")
    
    try:
        portfolio_chart = dashboard.create_portfolio_chart(days=1)
        print(f"Portfolio chart saved: {portfolio_chart}")
    except Exception as e:
        print(f"Portfolio chart creation failed: {e}")
    
    try:
        positions_chart = dashboard.create_positions_chart()
        print(f"Positions chart saved: {positions_chart}")
    except Exception as e:
        print(f"Positions chart creation failed: {e}")
    
    # Exportiere Daten
    export_path = dashboard.export_portfolio_data()
    print(f"Portfolio data exported: {export_path}")
    
 print("\n Dashboard test completed!")

if __name__ == "__main__":
    main()

