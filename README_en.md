# Metal Analyzer

A professional Python library for advanced analysis of precious metal prices (e.g., Gold). It provides high-precision trend prediction, market sentiment analysis, and sophisticated chart pattern detection.

## Key Features

- **👑 High-Precision Analysis Dashboard**: Integrates 4 key dimensions (Long-term Trend, Momentum, Volatility Acceleration, and Sentiment) to predict crashes and surges.
- **📈 Multi-Timeframe Support**: Supports Monthly, Weekly, Daily, 4-Hour, 1-Hour, and 15-Minute timeframes.
- **📊 Professional Charting**: Generates high-quality `mplfinance` charts in Dark Mode, automatically including EMA 20/50/200 and visual legends.
- **🔍 Pattern Detection**: Sensitive detection of Double Top (M-Top) patterns using advanced filtering techniques.

## Installation

```bash
cd metal-analyzer
pip install .
```

---

## Usage: 3 Main Demos

Three demo scripts are provided in the `examples/` folder to showcase the library's capabilities.

### 1. Comprehensive Analysis Demo (`examples/demo.py`)
Generates charts for all major timeframes and runs advanced trend prediction using the latest market data.

#### Code Example
```python
from metal_analyzer import MetalAnalyzer

analyzer = MetalAnalyzer(ticker="GC=F")
# Fetch data, add it to the analyzer, and run analyze_all()
# ... (See examples/demo.py for details)
analyzer.analyze_all()
```

#### Execution Result (Console Output)
```text
=== Metal Analyzer Comprehensive Analysis Demo ===
[1] Fetching data and generating charts...
[2] Running Advanced Trend Analysis
==================================================
   👑 High-Precision Gold Analysis Dashboard 👑
==================================================
【Long Trend】  Neutral / Consolidation
【Momentum】    Strong Downward Pressure
【Volatility】  Stable
【Sentiment】   Range Bound
--------------------------------------------------
 🎯 Final Prediction: Continuation Caution
 ⚠️ Risk Level:       Medium
 📝 Comment: Downward bias is strong, but a major acceleration hasn't triggered yet.
==================================================
```

#### Output Chart
![Daily Chart](docs/images/chart_daily.png)
*(Monthly, Weekly, Hourly, and 15M charts are also generated in bulk)*

---

### 2. Crash Acceleration Simulation (`examples/demo-20260130.py`)
Reproduces the historical crash of Jan 30, 2026, detecting the neckline break and the "Great Crash Acceleration" signal.

#### Execution Result (Console Output)
```text
==================================================
   👑 High-Precision Gold Analysis Dashboard 👑
==================================================
【Long Trend】  Neutral / Consolidation
【Momentum】    Strong Downward Pressure
【Volatility】  Stable
【Sentiment】   Neckline Breached (Crash Confirmed)
--------------------------------------------------
 🎯 Final Prediction: ⚠️ Great Crash Acceleration
 ⚠️ Risk Level:       EXTREME
 📝 Comment: Key support level broken. Volatility is spiking. Trend bottom is unknown.
==================================================
```

#### Output Chart
![Scenario 20260130](docs/images/20260130_chart_daily.png)

---

### 3. Bullish Trend Transition Simulation (`examples/demo-20251230.py`)
Reproduces the transition from range-bound to a bullish trend on Dec 30, 2025.

#### Execution Result (Console Output)
```text
==================================================
   👑 High-Precision Gold Analysis Dashboard 👑
==================================================
【Long Trend】  Neutral / Consolidation
【Momentum】    Calm
【Volatility】  Stable
【Sentiment】   Range Bound
--------------------------------------------------
 🎯 Final Prediction: Strong Floor / Rebound
 ⚠️ Risk Level:       Low
 📝 Comment: Buying pressure is dominant or a rebound at range bottom is observed.
==================================================
```

#### Output Chart
![Scenario 20251230](docs/images/20251230_chart_daily.png)

---

## Project Structure

Detailed descriptions of each file's role in the project.

| Folder | File | Description |
| :--- | :--- | :--- |
| `core/` | `analyzer.py` | Main `MetalAnalyzer` class. Orchestrates data management, analysis, and plotting. |
| `indicators/` | `sma.py` | Moving Average (SMA, EMA) calculation algorithms. |
| | `rsi.py` | Relative Strength Index (RSI) calculation algorithm. |
| `patterns/` | `double_top.py` | Double Top (M-Top) detection logic using SciPy filters. |
| `models/` | `advanced_predictor.py` | High-precision trend prediction engine based on 4 dashboards. |
| | `top_down.py` | Multi-timeframe top-down analysis logic. |
| | `signal_entry.py` | Entry and exit signal determination logic. |
| `examples/` | `demo.py` | Comprehensive analysis demo script using the latest market data. |
| | `demo-20260130.py` | Simulation script for the Jan 2026 crash scenario. |
| | `demo-20251230.py` | Simulation script for the Dec 2025 trend transition scenario. |
