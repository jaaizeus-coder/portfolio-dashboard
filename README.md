# Poseidon Dashboard 🔱

**Professional financial dashboard** - Real-time market data, technical analysis, portfolio tracking

## Quick Start

```bash
# Clone and setup
git clone https://github.com/jaaizeus-coder/portfolio-dashboard.git
cd portfolio-dashboard

# Start development server
./dev-tools/server.sh start

# Open dashboard
open http://localhost:8080
```

## Features

- **Real-time market data** via Finnhub API
- **Technical analysis** — RSI, MACD, Bollinger Bands
- **Portfolio tracking** — equities, crypto, ETFs, indices  
- **AI-powered briefings** via Anthropic Claude
- **Professional charts** with Chart.js
- **Responsive design** — works on mobile
- **Dark theme** with glassmorphism effects

## Development

### Server Management
```bash
./dev-tools/server.sh start     # Start on localhost:8080
./dev-tools/server.sh stop      # Stop server  
./dev-tools/server.sh restart   # Restart server
./dev-tools/server.sh status    # Check status
```

### API Configuration
```bash
./dev-tools/setup-keys.sh       # Setup instructions

# Edit these in index.html:
const FINNHUB_KEY = 'your_key_here';     # Get at finnhub.io
const ANTHROPIC_KEY = 'your_key_here';   # Get at console.anthropic.com
```

### Development Workflow
```bash
./dev-tools/backup.sh           # Create backup before changes
# Edit index.html
./dev-tools/deploy.sh           # Deploy to GitHub Pages
```

## Architecture

- **Single-page app** — Pure HTML/CSS/JavaScript (170KB)
- **No dependencies** — Except Chart.js and Inter font
- **Modular design** — Clean separation of data/rendering/UI
- **API-driven** — Finnhub + Anthropic integration
- **Client-side only** — Runs entirely in browser

## Portfolio Configuration

Current tracked assets (edit in `index.html`):

**Equities:** AAPL, ARKB, BROS, COIN, F, META, NVDA, PLTR, TSLA, FXAIX  
**Crypto:** BTC, ETH, SOL, BNB  
**Indices:** SPY, QQQ, IWM, DIA  
**Sectors:** XLK, XLF, XLV, XLY, XLE, XLI, XLB, XLRE, XLU, XLP, XLC  

## Live Demo

🚀 **https://jaaizeus-coder.github.io/portfolio-dashboard/**

## License

MIT — Built by Zeus ⚡