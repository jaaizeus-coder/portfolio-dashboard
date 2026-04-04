#!/usr/bin/env python3
"""
Poseidon Smart Alerts System
Real-time monitoring with intelligent notifications
"""
import sys, os, json, time, subprocess
sys.path.insert(0, '/Users/jaai/Library/Python/3.9/lib/python/site-packages')

import yfinance as yf
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

# Alert Configuration
ALERT_CONFIG = {
    "price_change_threshold": 5.0,  # Alert if price moves > 5%
    "volume_spike_multiplier": 3.0,  # Alert if volume > 3x average
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "check_interval": 30,  # seconds
    "email_cooldown": 300,  # 5 minutes between emails for same alert
    "max_alerts_per_hour": 10
}

EMAIL_CONFIG = {
    "from": "jaaizeus@gmail.com", 
    "to": "johnnyathans2016@gmail.com",
    "keychain_service": "zeus-gmail-smtp"
}

# Portfolio from briefing config
MONITORED_SYMBOLS = ["AAPL", "ARKB", "BROS", "COIN", "F", "META", "NVDA", "PLTR", "TSLA", "FXAIX", "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]

class AlertSystem:
    def __init__(self):
        self.alerts_sent = {}  # Track sent alerts to avoid spam
        self.last_prices = {}  # Track price history
        self.email_count = 0
        self.hour_start = datetime.now().hour
        
    def check_price_alerts(self, symbol, current_price, prev_price):
        """Check for significant price movements"""
        if prev_price is None or prev_price == 0:
            return []
        
        change_pct = ((current_price - prev_price) / prev_price) * 100
        alerts = []
        
        if abs(change_pct) >= ALERT_CONFIG["price_change_threshold"]:
            direction = "surged" if change_pct > 0 else "dropped"
            alert = {
                "type": "price_move",
                "symbol": symbol,
                "message": f"{symbol} {direction} {abs(change_pct):.1f}% to ${current_price:.2f}",
                "severity": "high" if abs(change_pct) > 10 else "medium",
                "price": current_price,
                "change_pct": change_pct
            }
            alerts.append(alert)
            
        return alerts
    
    def check_volume_alerts(self, symbol, current_volume, avg_volume):
        """Check for unusual volume spikes"""
        if avg_volume is None or avg_volume == 0:
            return []
            
        volume_ratio = current_volume / avg_volume
        alerts = []
        
        if volume_ratio >= ALERT_CONFIG["volume_spike_multiplier"]:
            alert = {
                "type": "volume_spike",
                "symbol": symbol,
                "message": f"{symbol} volume spike: {volume_ratio:.1f}x normal volume",
                "severity": "medium",
                "volume": current_volume,
                "ratio": volume_ratio
            }
            alerts.append(alert)
            
        return alerts
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI for overbought/oversold alerts"""
        if len(prices) < period + 1:
            return None
            
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def check_rsi_alerts(self, symbol, prices):
        """Check for RSI overbought/oversold conditions"""
        rsi = self.calculate_rsi(prices)
        if rsi is None:
            return []
            
        alerts = []
        
        if rsi <= ALERT_CONFIG["rsi_oversold"]:
            alert = {
                "type": "rsi_oversold",
                "symbol": symbol,
                "message": f"{symbol} RSI oversold: {rsi:.1f} (potential buy signal)",
                "severity": "medium",
                "rsi": rsi
            }
            alerts.append(alert)
        elif rsi >= ALERT_CONFIG["rsi_overbought"]:
            alert = {
                "type": "rsi_overbought", 
                "symbol": symbol,
                "message": f"{symbol} RSI overbought: {rsi:.1f} (potential sell signal)",
                "severity": "medium",
                "rsi": rsi
            }
            alerts.append(alert)
            
        return alerts
    
    def should_send_alert(self, alert):
        """Check if alert should be sent (avoid spam)"""
        alert_key = f"{alert['symbol']}_{alert['type']}"
        now = time.time()
        
        # Check email rate limits
        current_hour = datetime.now().hour
        if current_hour != self.hour_start:
            self.email_count = 0
            self.hour_start = current_hour
            
        if self.email_count >= ALERT_CONFIG["max_alerts_per_hour"]:
            return False
        
        # Check cooldown period
        if alert_key in self.alerts_sent:
            if now - self.alerts_sent[alert_key] < ALERT_CONFIG["email_cooldown"]:
                return False
        
        self.alerts_sent[alert_key] = now
        return True
    
    def send_alert_email(self, alert):
        """Send alert via email"""
        try:
            # Get app password
            result = subprocess.run(['security','find-generic-password','-a',EMAIL_CONFIG["from"],'-s',EMAIL_CONFIG["keychain_service"],'-w'], 
                                   capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Failed to get email password", file=sys.stderr)
                return False
            
            password = result.stdout.strip()
            
            # Create email
            subject = f"🚨 Poseidon Alert: {alert['symbol']} - {alert['type'].replace('_', ' ').title()}"
            
            emoji_map = {
                "price_move": "📈" if alert.get('change_pct', 0) > 0 else "📉",
                "volume_spike": "📊", 
                "rsi_oversold": "💚",
                "rsi_overbought": "🔴"
            }
            
            emoji = emoji_map.get(alert['type'], '⚠️')
            
            body = f"""
{emoji} POSEIDON ALERT

{alert['message']}

Alert Type: {alert['type'].replace('_', ' ').title()}
Severity: {alert['severity'].upper()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}

---
This alert was generated by the Poseidon monitoring system.
Dashboard: http://localhost:8080

Zeus ⚡
            """.strip()
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = EMAIL_CONFIG["from"]
            msg['To'] = EMAIL_CONFIG["to"]
            
            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL_CONFIG["from"], password)
                server.sendmail(EMAIL_CONFIG["from"], EMAIL_CONFIG["to"], msg.as_string())
            
            self.email_count += 1
            print(f"Alert sent: {alert['message']}", file=sys.stderr)
            return True
            
        except Exception as e:
            print(f"Failed to send alert email: {e}", file=sys.stderr)
            return False
    
    def save_alert_to_dashboard(self, alert):
        """Save alert data for dashboard consumption"""
        alerts_file = "/Users/jaai/.openclaw/workspace/poseidon-dashboard/alerts.json"
        
        try:
            # Load existing alerts
            if os.path.exists(alerts_file):
                with open(alerts_file, 'r') as f:
                    alerts_data = json.load(f)
            else:
                alerts_data = {"alerts": [], "last_updated": None}
            
            # Add new alert
            alert["timestamp"] = datetime.now().isoformat()
            alerts_data["alerts"].insert(0, alert)
            
            # Keep only last 50 alerts
            alerts_data["alerts"] = alerts_data["alerts"][:50]
            alerts_data["last_updated"] = datetime.now().isoformat()
            
            # Save alerts
            with open(alerts_file, 'w') as f:
                json.dump(alerts_data, f, indent=2)
                
            print(f"Alert saved to dashboard: {alert['symbol']} - {alert['type']}", file=sys.stderr)
            
        except Exception as e:
            print(f"Failed to save alert to dashboard: {e}", file=sys.stderr)
    
    def monitor_symbol(self, symbol):
        """Monitor a single symbol for alerts"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d", interval="1m")
            
            if len(hist) == 0:
                return []
            
            current_price = float(hist['Close'].iloc[-1])
            current_volume = float(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0
            
            # Get previous price for comparison
            prev_price = self.last_prices.get(symbol)
            self.last_prices[symbol] = current_price
            
            # Calculate average volume (last 20 periods)
            avg_volume = float(hist['Volume'].tail(20).mean()) if 'Volume' in hist and len(hist) >= 20 else current_volume
            
            # Get price history for RSI
            prices = hist['Close'].tolist()
            
            alerts = []
            
            # Check all alert types
            alerts.extend(self.check_price_alerts(symbol, current_price, prev_price))
            alerts.extend(self.check_volume_alerts(symbol, current_volume, avg_volume))
            alerts.extend(self.check_rsi_alerts(symbol, prices))
            
            return alerts
            
        except Exception as e:
            print(f"Error monitoring {symbol}: {e}", file=sys.stderr)
            return []
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle for all symbols"""
        print(f"🔍 Monitoring cycle started: {datetime.now().strftime('%H:%M:%S')}", file=sys.stderr)
        
        all_alerts = []
        
        for symbol in MONITORED_SYMBOLS:
            symbol_alerts = self.monitor_symbol(symbol)
            all_alerts.extend(symbol_alerts)
        
        # Process alerts
        high_priority_alerts = []
        for alert in all_alerts:
            # Save to dashboard
            self.save_alert_to_dashboard(alert)
            
            # Check if we should send email
            if self.should_send_alert(alert):
                if alert['severity'] in ['high', 'medium']:
                    high_priority_alerts.append(alert)
                    self.send_alert_email(alert)
        
        if all_alerts:
            print(f"📊 Alerts generated: {len(all_alerts)} total, {len(high_priority_alerts)} sent", file=sys.stderr)
        else:
            print(f"✅ No alerts triggered", file=sys.stderr)
        
        return all_alerts
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring loop"""
        print(f"🚨 Poseidon Alert System Started", file=sys.stderr)
        print(f"Monitoring {len(MONITORED_SYMBOLS)} symbols every {ALERT_CONFIG['check_interval']} seconds", file=sys.stderr)
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(ALERT_CONFIG["check_interval"])
                
        except KeyboardInterrupt:
            print(f"🛑 Alert system stopped by user", file=sys.stderr)
        except Exception as e:
            print(f"💥 Alert system error: {e}", file=sys.stderr)

def main():
    alert_system = AlertSystem()
    
    if "--daemon" in sys.argv:
        alert_system.run_continuous_monitoring()
    else:
        # Single monitoring cycle
        alerts = alert_system.run_monitoring_cycle()
        print(f"Monitoring complete: {len(alerts)} alerts generated")

if __name__ == "__main__":
    main()