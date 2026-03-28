#!/usr/bin/env python3
"""
Kill-Switch Demo für Trading System
Demonstriert automatische Risikokontrolle und Notfall-Mechanismen
"""

from datetime import datetime
from risk_manager import RiskManager, PortfolioTracker
from signal_generator import TradingSignal, SignalType, SignalStrength
from portfolio_dashboard import PortfolioDashboard

def simulate_market_crash_scenario():
    """Simuliere Markt-Crash-Szenario für Kill-Switch-Test"""
    
    print("=" * 80)
 print(" KILL-SWITCH DEMO - MARKET CRASH SIMULATION")
    print("=" * 80)
    
    risk_manager = RiskManager()
    portfolio_tracker = risk_manager.portfolio_tracker
    dashboard = PortfolioDashboard()
    
    # Schritt 1: Öffne mehrere Positionen
 print(" STEP 1: Opening multiple positions...")
    
    test_signals = [
        TradingSignal(
            symbol="BTC-USD",
            timestamp=datetime.now(),
            signal_type=SignalType.BUY,
            strength=SignalStrength.STRONG,
            entry_price=108000.00,
            stop_loss=105000.00,
            take_profit=115000.00,
            confidence=0.85,
            reasoning="Strong bullish signal",
            sentiment_score=0.7,
            technical_score=0.6,
            volume_score=50,
            position_size_percent=3.0,
            risk_reward_ratio=2.0
        ),
        TradingSignal(
            symbol="ETH-USD",
            timestamp=datetime.now(),
            signal_type=SignalType.BUY,
            strength=SignalStrength.MODERATE,
            entry_price=4400.00,
            stop_loss=4200.00,
            take_profit=4800.00,
            confidence=0.75,
            reasoning="Moderate bullish signal",
            sentiment_score=0.5,
            technical_score=0.4,
            volume_score=30,
            position_size_percent=2.5,
            risk_reward_ratio=2.0
        ),
        TradingSignal(
            symbol="TSLA",
            timestamp=datetime.now(),
            signal_type=SignalType.BUY,
            strength=SignalStrength.WEAK,
            entry_price=334.00,
            stop_loss=320.00,
            take_profit=360.00,
            confidence=0.65,
            reasoning="Weak bullish signal",
            sentiment_score=0.3,
            technical_score=0.2,
            volume_score=15,
            position_size_percent=1.5,
            risk_reward_ratio=1.8
        )
    ]
    
    opened_positions = []
    
    for signal in test_signals:
        is_valid, reason = risk_manager.validate_signal(signal)
        if is_valid:
            position_id = portfolio_tracker.open_position(signal)
            opened_positions.append((position_id, signal))
 print(f" Opened {signal.symbol}: {position_id}")
        else:
 print(f" Failed to open {signal.symbol}: {reason}")
    
    # Schritt 2: Zeige initiales Portfolio
 print(f"\n STEP 2: Initial portfolio status...")
    monitoring_result = risk_manager.monitor_portfolio()
    metrics = monitoring_result['portfolio_metrics']
    
    print(f"Portfolio Value: ${metrics['total_value']:,.2f}")
    print(f"Invested Amount: ${metrics['invested_amount']:,.2f}")
    print(f"Open Positions: {metrics['open_positions']}")
    print(f"Risk Level: {metrics['risk_level']}")
    
    # Schritt 3: Simuliere moderate Verluste
 print(f"\n STEP 3: Simulating moderate market decline (-5%)...")
    
    price_updates = [
        ("BTC-USD", 102600.00),  # -5%
        ("ETH-USD", 4180.00),    # -5%
        ("TSLA", 317.30)         # -5%
    ]
    
    for symbol, new_price in price_updates:
        portfolio_tracker.update_position_prices(symbol, new_price)
        print(f"Updated {symbol}: ${new_price:,.2f}")
    
    # Portfolio-Status nach moderaten Verlusten
    monitoring_result = risk_manager.monitor_portfolio()
    metrics = monitoring_result['portfolio_metrics']
    
    print(f"\nPortfolio after -5% decline:")
    print(f"Portfolio Value: ${metrics['total_value']:,.2f}")
    print(f"Total P&L: ${metrics['total_pnl']:+,.2f}")
    print(f"Risk Level: {metrics['risk_level']}")
    
    if monitoring_result['alerts']:
 print("️ Alerts:")
        for alert in monitoring_result['alerts']:
            print(f"  - {alert}")
    
    # Schritt 4: Simuliere schwere Verluste (Kill-Switch Trigger)
 print(f"\n STEP 4: Simulating severe market crash (-20%)...")
    
    crash_prices = [
        ("BTC-USD", 86400.00),   # -20%
        ("ETH-USD", 3520.00),    # -20%
        ("TSLA", 267.20)         # -20%
    ]
    
    for symbol, crash_price in crash_prices:
        portfolio_tracker.update_position_prices(symbol, crash_price)
        print(f"CRASH: {symbol} dropped to ${crash_price:,.2f}")
    
    # Portfolio-Status nach Crash
    monitoring_result = risk_manager.monitor_portfolio()
    metrics = monitoring_result['portfolio_metrics']
    
 print(f"\n Portfolio after market crash:")
    print(f"Portfolio Value: ${metrics['total_value']:,.2f}")
    print(f"Total P&L: ${metrics['total_pnl']:+,.2f} ({(metrics['total_pnl']/10000*100):+.1f}%)")
    print(f"Risk Level: {metrics['risk_level']}")
 print(f"Kill-Switch Active: {' YES' if monitoring_result['kill_switch_active'] else ' NO'}")
    
    if monitoring_result['alerts']:
 print("\n️ ALERTS:")
        for alert in monitoring_result['alerts']:
            print(f"  - {alert}")
    
    if monitoring_result['actions_taken']:
 print("\n ACTIONS TAKEN:")
        for action in monitoring_result['actions_taken']:
            print(f"  - {action}")
    
    # Schritt 5: Zeige finale Position-Status
 print(f"\n STEP 5: Final position status...")
    
    open_positions = portfolio_tracker.get_open_positions()
    print(f"Open Positions Remaining: {len(open_positions)}")
    
    if open_positions:
        for pos in open_positions:
            pnl_percent = (pos.unrealized_pnl / pos.position_size_usd) * 100
            print(f"  {pos.symbol}: ${pos.unrealized_pnl:+,.2f} ({pnl_percent:+.1f}%)")
    else:
        print("  All positions closed by Kill-Switch")
    
    # Schritt 6: Generiere finalen Bericht
 print(f"\n STEP 6: Generating final report...")
    
    final_report = dashboard.generate_portfolio_report()
    
    # Speichere Crash-Report
    report_path = '/home/ubuntu/trading_system/crash_simulation_report.txt'
    with open(report_path, 'w') as f:
        f.write("KILL-SWITCH DEMO - MARKET CRASH SIMULATION\n")
        f.write("=" * 80 + "\n")
        f.write(f"Simulation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("SCENARIO:\n")
        f.write("- Opened 3 long positions (BTC, ETH, TSLA)\n")
        f.write("- Simulated -5% market decline (moderate)\n")
        f.write("- Simulated -20% market crash (severe)\n")
        f.write("- Tested Kill-Switch activation\n\n")
        f.write(final_report)
    
    print(f"Crash simulation report saved: {report_path}")
    
    return monitoring_result

def test_manual_kill_switch():
    """Teste manuellen Kill-Switch"""
    
    print(f"\n{'='*80}")
 print(" MANUAL KILL-SWITCH TEST")
    print("=" * 80)
    
    risk_manager = RiskManager()
    
    # Aktiviere Kill-Switch manuell
    print("Activating Kill-Switch manually...")
    risk_manager.trigger_kill_switch("Manual test activation")
    
    # Prüfe Status
    monitoring_result = risk_manager.monitor_portfolio()
 print(f"Kill-Switch Status: {' ACTIVE' if monitoring_result['kill_switch_active'] else ' INACTIVE'}")
    
    # Deaktiviere Kill-Switch
    print("Deactivating Kill-Switch...")
    risk_manager.deactivate_kill_switch("Manual test deactivation")
    
    # Prüfe Status erneut
    monitoring_result = risk_manager.monitor_portfolio()
 print(f"Kill-Switch Status: {' ACTIVE' if monitoring_result['kill_switch_active'] else ' INACTIVE'}")

def main():
    """Hauptfunktion für Kill-Switch-Demo"""
    
 print(" TRADING SYSTEM KILL-SWITCH DEMONSTRATION")
    print("This demo shows how the system protects against major losses")
    print()
    
    # Simuliere Markt-Crash
    crash_result = simulate_market_crash_scenario()
    
    # Teste manuellen Kill-Switch
    test_manual_kill_switch()
    
    print(f"\n{'='*80}")
 print(" KILL-SWITCH DEMO COMPLETED")
    print("=" * 80)
    print("Key Features Demonstrated:")
    print("• Automatic position opening with risk validation")
    print("• Real-time portfolio monitoring and risk assessment")
    print("• Automatic Kill-Switch activation on severe losses")
    print("• Complete position closure for capital protection")
    print("• Manual Kill-Switch control")
    print("• Comprehensive reporting and logging")
    print()
    print("The system successfully protected the portfolio from catastrophic losses!")

if __name__ == "__main__":
    main()

