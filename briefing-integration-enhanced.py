#!/usr/bin/env python3
"""
Enhanced Poseidon-Briefing Integration
Adds news integration and trending analysis
"""
import sys, os
sys.path.insert(0, '/Users/jaai/Library/Python/3.9/lib/python/site-packages')

import yfinance as yf
import json, subprocess, base64, urllib.request, urllib.parse, re
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Enhanced configuration
PORTFOLIO_CONFIG = {
    "equities": ["AAPL", "ARKB", "BROS", "COIN", "F", "META", "NVDA", "PLTR", "TSLA", "FXAIX"],
    "crypto": {"BTC-USD": "BTC", "ETH-USD": "ETH", "SOL-USD": "SOL", "BNB-USD": "BNB"},
    "indices": ["SPY", "QQQ", "IWM", "DIA"],
    "sectors": ["XLK", "XLF", "XLV", "XLY", "XLE", "XLI", "XLB", "XLRE", "XLU", "XLP", "XLC"],
    "trending": {
        "growth": ["NVDA", "META", "GOOGL", "AMZN", "TSLA", "MSFT"],
        "value": ["BRK-B", "JPM", "WMT", "PG", "KO", "JNJ"],
        "momentum": ["QQQ", "SPY", "VTI", "IWM", "EFA", "EEM"],
        "crypto": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "ADA-USD", "DOT-USD"]
    }
}

EMAIL_CONFIG = {
    "from": "jaaizeus@gmail.com",
    "to": "johnnyathans2016@gmail.com",
    "keychain_service": "zeus-gmail-smtp"
}

def fetch_news_for_symbol(symbol, max_articles=3):
    """Fetch news articles for a symbol"""
    try:
        ticker = yf.Ticker(symbol.replace('-USD', ''))  # Remove crypto suffix for news
        news = ticker.news
        
        if not news:
            return []
        
        articles = []
        for item in news[:max_articles]:
            # Clean up the news data
            title = item.get('title', '')
            link = item.get('link', '')
            publisher = item.get('publisher', '')
            pub_time = item.get('providerPublishTime', 0)
            
            # Format publish time
            if pub_time:
                try:
                    pub_date = datetime.fromtimestamp(pub_time)
                    time_str = pub_date.strftime("%m/%d %H:%M")
                except:
                    time_str = "Recent"
            else:
                time_str = "Recent"
            
            articles.append({
                'title': title[:100] + '...' if len(title) > 100 else title,
                'url': link,
                'publisher': publisher,
                'time': time_str
            })
        
        return articles
        
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}", file=sys.stderr)
        return []

def fetch_trending_analysis():
    """Fetch trending investment data across categories"""
    trending_data = {
        "growth_stocks": {},
        "value_stocks": {},
        "momentum_etfs": {},
        "crypto": {},
        "summary": {
            "top_performer": None,
            "biggest_mover": None,
            "highest_volume": None
        }
    }
    
    print("Fetching trending analysis...", file=sys.stderr)
    
    all_positions = []
    
    # Fetch growth stocks
    for ticker in PORTFOLIO_CONFIG["trending"]["growth"]:
        print(f"  Growth: {ticker}...", file=sys.stderr)
        data = fetch_basic_data(ticker, "growth")
        if data:
            trending_data["growth_stocks"][ticker] = data
            all_positions.append(data)
    
    # Fetch value stocks
    for ticker in PORTFOLIO_CONFIG["trending"]["value"]:
        print(f"  Value: {ticker}...", file=sys.stderr)
        data = fetch_basic_data(ticker, "value")
        if data:
            trending_data["value_stocks"][ticker] = data
            all_positions.append(data)
    
    # Fetch momentum ETFs
    for ticker in PORTFOLIO_CONFIG["trending"]["momentum"]:
        print(f"  Momentum: {ticker}...", file=sys.stderr)
        data = fetch_basic_data(ticker, "momentum")
        if data:
            trending_data["momentum_etfs"][ticker] = data
            all_positions.append(data)
    
    # Fetch crypto
    for symbol in PORTFOLIO_CONFIG["trending"]["crypto"]:
        display_name = symbol.replace('-USD', '')
        print(f"  Crypto: {display_name}...", file=sys.stderr)
        data = fetch_basic_data(symbol, "crypto")
        if data:
            data['symbol'] = display_name  # Use clean symbol for display
            trending_data["crypto"][display_name] = data
            all_positions.append(data)
    
    # Calculate summary stats
    if all_positions:
        # Top performer by percentage
        top_performer = max(all_positions, key=lambda x: x.get('change_pct', -999))
        trending_data["summary"]["top_performer"] = top_performer
        
        # Biggest absolute mover
        biggest_mover = max(all_positions, key=lambda x: abs(x.get('change_pct', 0)))
        trending_data["summary"]["biggest_mover"] = biggest_mover
        
        # Highest volume
        highest_volume = max(all_positions, key=lambda x: x.get('volume', 0))
        trending_data["summary"]["highest_volume"] = highest_volume
    
    return trending_data

def fetch_basic_data(ticker, category="equity"):
    """Fetch basic price/volume data for trending analysis"""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        hist = t.history(period="5d")
        
        if len(hist) == 0:
            return None
        
        prices = list(hist['Close'].values)
        volumes = list(hist['Volume'].values)
        
        price = prices[-1] if prices else 0
        prev_close = info.get('regularMarketPreviousClose') or (prices[-2] if len(prices) > 1 else price)
        change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0
        
        # Calculate 5-day momentum
        momentum_5d = ((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) >= 5 else 0
        
        return {
            'symbol': ticker,
            'name': info.get('shortName', ticker),
            'price': round(price, 2),
            'change_pct': round(change_pct, 2),
            'volume': volumes[-1] if volumes else 0,
            'market_cap': info.get('marketCap', 0),
            'momentum_5d': round(momentum_5d, 2),
            'category': category,
            'sector': info.get('sector', ''),
            'avg_volume': sum(volumes) / len(volumes) if volumes else 0
        }
        
    except Exception as e:
        print(f"Error fetching {ticker}: {e}", file=sys.stderr)
        return None

def fetch_portfolio_data():
    """Enhanced portfolio data fetch with news"""
    now = datetime.now()
    
    portfolio_data = {
        "timestamp": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "date_formatted": now.strftime("%B %d, %Y").replace(" 0", " "),
        "day": now.strftime("%A"),
        "equities": {},
        "crypto": {},
        "trending": {},
        "news": {},
        "summary": {
            "top_gainers": [],
            "top_losers": [],
            "total_positions": 0,
            "positions_up": 0,
            "positions_down": 0
        }
    }
    
    print("Fetching enhanced portfolio data...", file=sys.stderr)
    
    # Fetch equities with news
    for ticker in PORTFOLIO_CONFIG["equities"]:
        print(f"  Equity: {ticker}...", file=sys.stderr)
        try:
            t = yf.Ticker(ticker)
            info = t.info or {}
            hist = t.history(period="12d")
            
            prices = list(hist['Close'].values[-10:]) if len(hist) > 0 else []
            labels = [d.strftime("%m/%d") for d in hist.index[-10:]] if len(hist) > 0 else []
            
            price = info.get('regularMarketPrice') or info.get('currentPrice') or (prices[-1] if prices else 0)
            prev = info.get('regularMarketPreviousClose') or info.get('previousClose') or (prices[-2] if len(prices) > 1 else price)
            change_pct = ((price - prev) / prev * 100) if prev else 0
            
            # Fetch news for this symbol
            news_articles = fetch_news_for_symbol(ticker)
            
            portfolio_data["equities"][ticker] = {
                "symbol": ticker,
                "name": info.get('shortName', ticker),
                "price": round(price, 2) if price else 0,
                "change_pct": round(change_pct, 2),
                "volume": info.get('regularMarketVolume') or info.get('volume') or 0,
                "market_cap": info.get('marketCap', 0),
                "high_52w": info.get('fiftyTwoWeekHigh', 0),
                "low_52w": info.get('fiftyTwoWeekLow', 0),
                "recommendation": info.get('recommendationKey', ''),
                "target_price": info.get('targetMeanPrice', 0),
                "earnings_date": str(info.get('earningsDate', '')),
                "prices_10d": [round(p, 2) for p in prices],
                "labels_10d": labels,
                "sector": info.get('sector', ''),
                "industry": info.get('industry', ''),
                "news": news_articles
            }
            
            # Store news separately for email template
            if news_articles:
                portfolio_data["news"][ticker] = news_articles
                
        except Exception as e:
            print(f"Error fetching {ticker}: {e}", file=sys.stderr)
            portfolio_data["equities"][ticker] = {"symbol": ticker, "error": str(e)}
    
    # Fetch crypto with news
    for symbol, display_name in PORTFOLIO_CONFIG["crypto"].items():
        print(f"  Crypto: {display_name}...", file=sys.stderr)
        try:
            t = yf.Ticker(symbol)
            info = t.info or {}
            hist = t.history(period="12d")
            
            prices = list(hist['Close'].values[-10:]) if len(hist) > 0 else []
            labels = [d.strftime("%m/%d") for d in hist.index[-10:]] if len(hist) > 0 else []
            
            price = info.get('regularMarketPrice') or info.get('currentPrice') or (prices[-1] if prices else 0)
            prev = info.get('regularMarketPreviousClose') or info.get('previousClose') or (prices[-2] if len(prices) > 1 else price)
            change_pct = ((price - prev) / prev * 100) if prev else 0
            
            # Fetch crypto news
            news_articles = fetch_news_for_symbol(display_name)
            
            portfolio_data["crypto"][display_name] = {
                "symbol": display_name,
                "name": f"{display_name} ({symbol.replace('-USD', '')})",
                "price": round(price, 2) if price else 0,
                "change_pct": round(change_pct, 2),
                "volume": info.get('regularMarketVolume') or info.get('volume') or 0,
                "market_cap": info.get('marketCap', 0),
                "prices_10d": [round(p, 2) for p in prices],
                "labels_10d": labels,
                "news": news_articles
            }
            
            # Store crypto news
            if news_articles:
                portfolio_data["news"][display_name] = news_articles
                
        except Exception as e:
            print(f"Error fetching {display_name}: {e}", file=sys.stderr)
            portfolio_data["crypto"][display_name] = {"symbol": display_name, "error": str(e)}
    
    # Fetch trending analysis
    portfolio_data["trending"] = fetch_trending_analysis()
    
    # Calculate portfolio summary
    all_positions = list(portfolio_data["equities"].values()) + list(portfolio_data["crypto"].values())
    valid_positions = [p for p in all_positions if "error" not in p and p.get("price", 0) > 0]
    
    portfolio_data["summary"]["total_positions"] = len(valid_positions)
    portfolio_data["summary"]["positions_up"] = len([p for p in valid_positions if p.get("change_pct", 0) > 0])
    portfolio_data["summary"]["positions_down"] = len([p for p in valid_positions if p.get("change_pct", 0) < 0])
    
    # Top gainers and losers
    sorted_positions = sorted(valid_positions, key=lambda x: x.get("change_pct", 0), reverse=True)
    portfolio_data["summary"]["top_gainers"] = sorted_positions[:3]
    portfolio_data["summary"]["top_losers"] = sorted_positions[-3:]
    
    return portfolio_data

def generate_dashboard_data(portfolio_data):
    """Convert portfolio data to enhanced dashboard format"""
    dashboard_data = {
        "timestamp": portfolio_data["timestamp"],
        "briefing_data": {
            "date": portfolio_data["date_formatted"],
            "day": portfolio_data["day"],
            "summary": portfolio_data["summary"],
            "positions": {},
            "trending": portfolio_data["trending"],
            "news": portfolio_data["news"]
        }
    }
    
    # Combine all positions for dashboard
    all_positions = {}
    all_positions.update(portfolio_data["equities"])
    all_positions.update(portfolio_data["crypto"])
    
    dashboard_data["briefing_data"]["positions"] = all_positions
    
    return dashboard_data

def generate_briefing_email(portfolio_data):
    """Generate enhanced HTML email with news links"""
    DATE_STR = portfolio_data["date_formatted"]
    DAY_STR = portfolio_data["day"]
    now = datetime.now()
    TIME_STR = now.strftime("%I:%M %p %Z")
    
    def fmt_price(p):
        if p >= 1000: return f"${p:,.2f}"
        return f"${p:.2f}"
    
    def fmt_vol(v):
        if v >= 1e9: return f"${v/1e9:.1f}B"
        if v >= 1e6: return f"${v/1e6:.1f}M"
        if v >= 1e3: return f"${v/1e3:.0f}K"
        return f"${v:.0f}"
    
    def chart_url(prices, labels, positive):
        if not prices or not labels:
            return ""
        
        color = "#22c55e" if positive else "#ef4444"
        bg = f"rgba({'34,197,94' if positive else '239,68,68'},0.12)"
        
        cfg = {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": [{
                    "data": prices,
                    "borderColor": color,
                    "backgroundColor": bg,
                    "fill": True, "tension": 0.4,
                    "pointRadius": 2, "pointBackgroundColor": color,
                    "borderWidth": 2.5
                }]
            },
            "options": {
                "plugins": {"legend": {"display": False}},
                "scales": {
                    "x": {"grid": {"color": "rgba(255,255,255,0.04)", "borderColor": "transparent"},
                           "ticks": {"color": "#6b7280", "font": {"size": 9}, "maxRotation": 0}},
                    "y": {"grid": {"color": "rgba(255,255,255,0.04)", "borderColor": "transparent"},
                           "ticks": {"color": "#6b7280", "font": {"size": 9}}}
                },
                "backgroundColor": "#111827",
                "layout": {"padding": {"left": 4, "right": 4, "top": 8, "bottom": 4}}
            }
        }
        encoded = urllib.parse.quote(json.dumps(cfg))
        return f"https://quickchart.io/chart?c={encoded}&w=560&h=110&bkg=%23111827&devicePixelRatio=2"
    
    def news_links_html(articles):
        """Generate news links HTML for position cards"""
        if not articles:
            return ""
        
        news_items = []
        for article in articles[:3]:  # Limit to 3 articles
            title = article.get('title', 'News Article')
            url = article.get('url', '#')
            publisher = article.get('publisher', 'Source')
            time_str = article.get('time', '')
            
            news_items.append(f'''
                <div style="margin:2px 0;padding:4px 0;border-bottom:1px solid #1e293b;">
                    <div style="font-size:11px;line-height:1.4;">
                        <a href="{url}" target="_blank" style="color:#93c5fd;text-decoration:none;">{title}</a>
                    </div>
                    <div style="font-size:9px;color:#6b7280;margin-top:2px;">
                        {publisher} • {time_str}
                    </div>
                </div>
            ''')
        
        if news_items:
            return f'''
                <div style="margin-top:12px;padding:8px;background:#111827;border-radius:6px;border:1px solid #1e3a5f;">
                    <div style="color:#60a5fa;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">📰 Latest News</div>
                    {''.join(news_items)}
                </div>
            '''
        return ""
    
    def position_card(symbol, data):
        if "error" in data:
            return f'<div style="background:#0f172a;border:2px solid #1e3a5f;border-radius:14px;padding:20px;margin-bottom:14px;"><div style="color:#f87171;">Error loading {symbol}</div></div>'
        
        change_color = "#00c853" if data.get('change_pct', 0) >= 0 else "#ff3d3d"
        arrow = "▲" if data.get('change_pct', 0) >= 0 else "▼"
        positive = data.get('change_pct', 0) >= 0
        
        chart = ""
        if data.get('prices_10d') and data.get('labels_10d'):
            chart = f'<img src="{chart_url(data["prices_10d"], data["labels_10d"], positive)}" width="100%" style="border-radius:8px;margin:12px 0 4px;display:block;" alt="chart" />'
        
        vol_str = fmt_vol(data.get('volume', 0)) if data.get('volume') else "—"
        h52_str = fmt_price(data.get('high_52w', 0)) if data.get('high_52w') else "—"
        
        # Add news links
        news_html = news_links_html(data.get('news', []))
        
        return f'''<div style="background:#0f172a;border:2px solid #1e3a5f;border-radius:14px;padding:20px;margin-bottom:14px;">
          <table width="100%" cellpadding="0" cellspacing="0"><tr>
            <td style="vertical-align:top;width:44%;">
              <div style="font-size:20px;font-weight:900;color:#ffffff;">{symbol}</div>
              <div style="font-size:28px;font-weight:800;color:#ffffff;margin:4px 0 2px;">{fmt_price(data.get('price', 0))}</div>
              <div style="font-size:15px;font-weight:700;color:{change_color};">{arrow} {data.get('change_pct', 0):+.2f}%</div>
            </td>
            <td style="text-align:right;">
              <div style="color:#9ca3af;font-size:11px;">Volume</div>
              <div style="color:#e5e7eb;font-size:13px;">{vol_str}</div>
            </td>
            <td style="text-align:right;">
              <div style="color:#9ca3af;font-size:11px;">52W High</div>
              <div style="color:#e5e7eb;font-size:13px;">{h52_str}</div>
            </td>
          </tr></table>
          {chart}
          {news_html}
        </div>'''
    
    # Build summary
    summary = portfolio_data["summary"]
    def summary_row(pos):
        c = "#00c853" if pos.get('change_pct', 0) >= 0 else "#ff3d3d"
        a = "▲" if pos.get('change_pct', 0) >= 0 else "▼"
        return f'''<tr>
          <td style="padding:8px 12px;color:#e5e7eb;font-weight:600;">{a} {pos.get('symbol', 'N/A')}</td>
          <td style="padding:8px 12px;color:#e5e7eb;">{fmt_price(pos.get('price', 0))}</td>
          <td style="padding:8px 12px;color:{c};font-weight:600;">{a} {pos.get('change_pct', 0):+.2f}%</td>
        </tr>'''
    
    g_rows = "".join(summary_row(s) for s in summary.get('top_gainers', []))
    l_rows = "".join(summary_row(s) for s in summary.get('top_losers', []))
    
    portfolio_summary = f'''<div style="background:#0f172a;border:2px solid #1e293b;border-radius:14px;padding:20px 22px;margin-bottom:16px;">
    <div style="color:#60a5fa;font-size:11px;text-transform:uppercase;letter-spacing:2px;font-weight:800;margin-bottom:16px;border-bottom:1px solid #1e293b;padding-bottom:10px;">📊 PORTFOLIO SUMMARY</div>
    <table width="100%" cellpadding="0" cellspacing="0"><tr>
      <td width="50%" style="vertical-align:top;padding-right:10px;">
        <div style="color:#4ade80;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">▲ TOP GAINERS</div>
        <table width="100%">{g_rows}</table>
      </td>
      <td width="50%" style="vertical-align:top;padding-left:10px;border-left:2px solid #1e293b;">
        <div style="color:#f87171;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">▼ TOP LOSERS</div>
        <table width="100%">{l_rows}</table>
      </td>
    </tr></table>
  </div>'''
    
    # Build email sections
    header = f'''<div style="background:linear-gradient(135deg,#1e3a8a 0%,#1e1b4b 50%,#0f172a 100%);border-radius:16px;padding:26px 28px;margin-bottom:16px;border:1px solid #3b82f6;">
    <table width="100%" cellpadding="0" cellspacing="0"><tr>
      <td>
        <div style="color:#93c5fd;font-size:10px;text-transform:uppercase;letter-spacing:3px;font-weight:700;">⚡ Daily Portfolio Briefing</div>
        <div style="color:#ffffff;font-size:28px;font-weight:900;margin:8px 0 4px;letter-spacing:-0.5px;">Good Morning, John ☀️</div>
        <div style="color:#7dd3fc;font-size:13px;font-weight:500;">{DAY_STR}, {DATE_STR} &nbsp;·&nbsp; {TIME_STR}</div>
      </td>
      <td style="text-align:right;vertical-align:top;">
        <div style="background:rgba(59,130,246,0.2);border:1px solid #3b82f6;border-radius:10px;padding:8px 14px;display:inline-block;">
          <div style="color:#60a5fa;font-size:12px;font-weight:800;text-transform:uppercase;">ZEUS ⚡</div>
          <div style="color:#94a3b8;font-size:10px;margin-top:2px;">AI Portfolio Assistant</div>
        </div>
      </td>
    </tr></table>
  </div>'''
    
    # Equity cards
    equity_cards = "".join(position_card(sym, data) for sym, data in portfolio_data["equities"].items())
    equities_section = f'''<div style="color:#60a5fa;font-size:11px;text-transform:uppercase;letter-spacing:2px;font-weight:800;margin:24px 0 12px;border-left:3px solid #3b82f6;padding-left:10px;">📈 EQUITIES & ETFs</div>
    {equity_cards}'''
    
    # Crypto cards
    crypto_cards = "".join(position_card(sym, data) for sym, data in portfolio_data["crypto"].items())
    crypto_section = f'''<div style="color:#f59e0b;font-size:11px;text-transform:uppercase;letter-spacing:2px;font-weight:800;margin:24px 0 12px;border-left:3px solid #f59e0b;padding-left:10px;">₿ CRYPTO</div>
    {crypto_cards}'''
    
    # Market resources + dashboard link
    resources = f'''<div style="background:#0f172a;border:2px solid #1e293b;border-radius:14px;padding:18px 22px;margin-bottom:16px;">
    <div style="color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;margin-bottom:10px;">🔗 Market Resources</div>
    <div style="font-size:13px;line-height:2.2;">
      <a href="http://localhost:8080" style="color:#60a5fa;text-decoration:none;margin-right:20px;">🔱 Poseidon Dashboard</a>
      <a href="https://finance.yahoo.com" style="color:#60a5fa;text-decoration:none;margin-right:20px;">Yahoo Finance</a>
      <a href="https://www.marketwatch.com" style="color:#60a5fa;text-decoration:none;margin-right:20px;">MarketWatch</a>
      <a href="https://www.bloomberg.com/markets" style="color:#60a5fa;text-decoration:none;">Bloomberg</a>
    </div>
  </div>'''
    
    # Footer
    footer = f'''<div style="text-align:center;padding:20px 0;color:#475569;font-size:12px;border-top:1px solid #1e293b;margin-top:8px;">
    <div style="margin-bottom:4px;">Report by <strong style="color:#60a5fa;">Zeus ⚡</strong> &nbsp;·&nbsp; {DAY_STR}, {DATE_STR}</div>
    <div>Enhanced with News Integration &nbsp;·&nbsp; Powered by Poseidon Dashboard &nbsp;·&nbsp; Not investment advice.</div>
  </div>'''
    
    html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
  body{{margin:0;padding:0;background:#0a0f1e;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}}
  a{{color:#60a5fa;}}
</style></head>
<body style="background:#0a0f1e;">
<div style="max-width:680px;margin:0 auto;background:#0a0f1e;padding:20px 14px;">
  {header}
  {portfolio_summary}
  {equities_section}
  {crypto_section}
  {resources}
  {footer}
</div>
</body></html>'''
    
    return html

def save_dashboard_data(dashboard_data):
    """Save enhanced data for dashboard consumption"""
    output_file = "/Users/jaai/.openclaw/workspace/poseidon-dashboard/briefing-data.json"
    
    try:
        # Convert numpy types to native Python types for JSON serialization
        def convert_types(obj):
            if hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(v) for v in obj]
            else:
                return obj
        
        clean_data = convert_types(dashboard_data)
        
        with open(output_file, 'w') as f:
            json.dump(clean_data, f, indent=2, default=str)  # default=str handles remaining edge cases
        print(f"Enhanced dashboard data saved: {output_file}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Error saving dashboard data: {e}", file=sys.stderr)
        return False

def send_email(html_content):
    """Send enhanced briefing email via SMTP"""
    try:
        # Get app password from Keychain
        result = subprocess.run(['security','find-generic-password','-a',EMAIL_CONFIG["from"],'-s',EMAIL_CONFIG["keychain_service"],'-w'], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to retrieve password from Keychain", file=sys.stderr)
            return False
        
        password = result.stdout.strip()
        
        # Build email
        subject = f"📊 Portfolio Briefing — {datetime.now().strftime('%b %-d, %Y')}"
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG["from"]
        msg['To'] = EMAIL_CONFIG["to"]
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send via SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(EMAIL_CONFIG["from"], password)
            s.sendmail(EMAIL_CONFIG["from"], EMAIL_CONFIG["to"], msg.as_string())
        
        print(f"Enhanced email sent: {subject}", file=sys.stderr)
        return True
        
    except Exception as e:
        print(f"Email sending failed: {e}", file=sys.stderr)
        return False

def main():
    """Enhanced integration main function"""
    print("🔱 Enhanced Poseidon-Briefing Integration", file=sys.stderr)
    print("=========================================", file=sys.stderr)
    
    # Fetch enhanced portfolio data
    portfolio_data = fetch_portfolio_data()
    
    # Generate enhanced dashboard data
    dashboard_data = generate_dashboard_data(portfolio_data)
    
    # Save data for dashboard
    dashboard_saved = save_dashboard_data(dashboard_data)
    
    # Generate and send email
    if "--email" in sys.argv or "--send" in sys.argv:
        html_content = generate_briefing_email(portfolio_data)
        email_sent = send_email(html_content)
        
        if email_sent:
            print("✅ Enhanced integration complete: Dashboard data saved, email sent", file=sys.stderr)
        else:
            print("⚠️ Enhanced integration partial: Dashboard data saved, email failed", file=sys.stderr)
    else:
        print("✅ Enhanced integration complete: Dashboard data saved (use --email to send)", file=sys.stderr)
    
    # Output summary
    summary = portfolio_data["summary"]
    trending_summary = portfolio_data["trending"]["summary"]
    top_performer = trending_summary.get("top_performer", {})
    
    print(f"Portfolio: {summary['total_positions']} positions, {summary['positions_up']} up, {summary['positions_down']} down")
    if top_performer:
        print(f"Trending leader: {top_performer.get('symbol', 'N/A')} ({top_performer.get('change_pct', 0):+.1f}%)")

if __name__ == "__main__":
    main()