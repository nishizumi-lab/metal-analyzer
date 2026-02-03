# Metal Analyzer

A professional Python library for advanced analysis of precious metal prices (e.g., Gold). It provides trend analysis, market sentiment analysis, and sophisticated chart pattern detection.

## Features

Feature|Description
--|--
Short-term Trend Analysis|Analyzes short-term price movements based on 4 key dimensions: Long-term Trend, Momentum, Volatility Acceleration, and Sentiment.
Multi-Timeframe Support|Generates 6 types of timeframe charts: Monthly, Weekly, Daily, 4H, 1H, and 15M. Visualizes trends with EMA 20/50/200 and Bollinger Bands.

## Algorithm Logic Verification

Comparison of how this library encodes professional trading strategies like "Crash Signs" and "Double Top Formation".

| Video Technique | Current Implementation |
| :--- | :--- |
| **Double Top (W-Top) Formation** | Uses `detect_double_top` function to identify two peaks within 3% price difference (using `scipy.signal.find_peaks`). |
| **Neckline Break** | Calculates the lowest point between two peaks (neckline) and returns "Detected (True)" if the current price drops below it. |
| **"Bulls getting burned" (Strong Sell)** | Upon detecting a neckline break, sets the sentiment score to **"-5 (Crash Confirmed)"**, applying a strong selling bias. |
| **Signs of Crash (Volatility Acceleration)** | Dashboard 3 triggers "Accelerating" if the recent range exceeds 1.5x the past average, amplifying the final score by **1.5x**. |
| **Great Crash Scenario** | If the total score drops below "-6", it outputs **`⚠️ Great Crash Acceleration`** as the final prediction. |

## Backtest Verification Results

Backtest results for recent periods with significant price volatility.
The model detected signs of "Crashes" with extremely high accuracy, but challenges remain in predicting "V-shaped Recoveries" after sharp drops.

| Date | Actual Movement | Prediction Result | Judgment |
| :--- | :--- | :--- | :--- |
| **2025-10-20** | Next Day -5.7% Drop | **⚠️ Great Crash Acceleration** | ⭕ **Success** |
| **2025-12-26** | Next Week -4.5% Drop | **Continuation Caution** | ⭕ **Partial Success** |
| **2026-01-29** | Next Day -11.3% Crash | **⚠️ Great Crash Acceleration** | ⭕ **Great Success** |
| **2026-02-02** | Next Day +6.9% Surge | **Continuation Caution** | ❌ **Fail** |


## Installation

```bash
pip install metal-analyzer
```

## Quick Start

### A. Short-term Trend Analysis (4 Dashboards)

```python
from metal_analyzer import MetalAnalyzer
import yfinance as yf

# Initialize
analyzer = MetalAnalyzer(ticker="GC=F")

# Prepare data (Daily, 4H, and 1H required)
d_df = yf.download("GC=F", period="2y", interval="1d")
h1_df = yf.download("GC=F", period="1mo", interval="1h")

analyzer.add_timeframe_data("Daily", d_df)
analyzer.add_timeframe_data("1h", h1_df)

# Run analysis
result = analyzer.analyze_short_trend()

print(f"Final Prediction: {result['final_prediction']}")
print(f"Risk Level: {result['risk_level']}")
```

### B. Multi-Timeframe Analysis (Top-Down)

```python
# Check alignment between Daily and Hourly
signal, prediction, d_trend, h_trend, h_rsi = analyzer.analyze_top_down()

print(f"Signal: {signal}")
print(f"Trend View: {prediction}")
```

### C. Chart Generation (with EMA & Bollinger Bands)

```python
# Save 1H chart
analyzer.plot_candlestick("1h", filename="chart_1h.png")
```

---

## Usage: 3 Main Demos

Three demo scripts are provided in the `examples/` folder to showcase the library's capabilities.

### 1. Comprehensive Analysis Demo (`examples/demo.py`)
Generates charts for all major timeframes and runs short-term trend analysis using the latest market data.

#### Execution Result (Console Output)
```text
=== Metal Analyzer Comprehensive Analysis Demo ===
[1] Fetching data and generating charts...
[2] Short-term Trend Analysis
==================================================
 ■ Short-term Trend Analysis
==================================================
【Long Trend:  Neutral / Consolidation
【Momentum:    Strong Downward Pressure
【Volatility:  Stable
【Sentiment】   Range Bound
--------------------------------------------------
 Final Prediction: Continuation Caution
 Risk Level:       Medium
 Comment: Downward bias is strong, but a major acceleration (crash) hasn't triggered yet.
==================================================
```

#### Output Charts (6 Timeframes)
<details>
<summary>Click to view all timeframe charts (6 images)</summary>

- **Monthly**
  ![Monthly](examples/outputs/candles/chart_monthly.png)
- **Weekly**
  ![Weekly](examples/outputs/candles/chart_weekly.png)
- **Daily**
  ![Daily](examples/outputs/candles/chart_daily.png)
- **4-Hour (4H)**
  ![4H](examples/outputs/candles/chart_4h.png)
- **1-Hour (1H)**
  ![1H](examples/outputs/candles/chart_1h.png)
- **15-Minute (15M)**
  ![15M](examples/outputs/candles/chart_15m.png)

</details>

---

### 2. Crash Acceleration Simulation (`examples/demo-20260130.py`)
Reproduces the historical crash of Jan 30, 2026, detecting the neckline break and the "Great Crash Acceleration" signal.

#### Execution Result (Console Output)
```text
==================================================
 ■ High-Precision Gold Analysis Dashboard
==================================================
【Long Trend:  Neutral / Consolidation
【Momentum:    Strong Downward Pressure
【Volatility:  Stable
【Sentiment】   Neckline Breached (High Risk of Crash)
--------------------------------------------------
 Final Prediction: ⚠️ Great Crash Acceleration
 Risk Level:       EXTREME
 Comment: Key support level broken. Volatility is spiking. Trend bottom is unknown.
==================================================
```

#### Output Charts (6 Timeframes)
<details>
<summary>Click to view all timeframe charts (6 images)</summary>

- **Monthly**
  ![Monthly](examples/outputs/candles/20260130_chart_monthly.png)
- **Weekly**
  ![Weekly](examples/outputs/candles/20260130_chart_weekly.png)
- **Daily**
  ![Daily](examples/outputs/candles/20260130_chart_daily.png)
- **4-Hour (4H)**
  ![4H](examples/outputs/candles/20260130_chart_4h.png)
- **1-Hour (1H)**
  ![1H](examples/outputs/candles/20260130_chart_1h.png)
- **15-Minute (15M)**
  ![15M](examples/outputs/candles/20260130_chart_15m.png)

</details>

---

### 3. Bullish Trend Transition Simulation (`examples/demo-20251230.py`)
Reproduces the transition from range-bound to a bullish trend on Dec 30, 2025.

#### Execution Result (Console Output)
```text
==================================================
 ■ High-Precision Gold Analysis Dashboard
==================================================
【Long Trend:  Neutral / Consolidation
【Momentum:    Calm
【Volatility:  Stable
【Sentiment】   Range Bound
--------------------------------------------------
 Final Prediction: Strong Floor / Rebound
 Risk Level:       Low
 Comment: Buying pressure is dominant or a rebound at range bottom is observed.
==================================================
```

#### Output Charts (6 Timeframes)
<details>
<summary>Click to view all timeframe charts (6 images)</summary>

- **Monthly**
  ![Monthly](examples/outputs/candles/20251230_chart_monthly.png)
- **Weekly**
  ![Weekly](examples/outputs/candles/20251230_chart_weekly.png)
- **Daily**
  ![Daily](examples/outputs/candles/20251230_chart_daily.png)
- **4-Hour (4H)**
  ![4H](examples/outputs/candles/20251230_chart_4h.png)
- **1-Hour (1H)**
  ![1H](examples/outputs/candles/20251230_chart_1h.png)
- **15-Minute (15M)**
  ![15M](examples/outputs/candles/20251230_chart_15m.png)

</details>

---

## Project Structure

Detailed descriptions of each file's role in the project.

| Folder | File | Description |
| :--- | :--- | :--- |
| `core/` | [`analyzer.py`](metal_analyzer/core/analyzer.py) | Main `MetalAnalyzer` class. Orchestrates data management, analysis, and plotting. |
| `indicators/` | [`sma.py`](metal_analyzer/indicators/sma.py) | Moving Average (SMA, EMA) calculation algorithms. |
| | [`bollinger_bands.py`](metal_analyzer/indicators/bollinger_bands.py) | Bollinger Bands calculation algorithm. |
| | [`rsi.py`](metal_analyzer/indicators/rsi.py) | Relative Strength Index (RSI) calculation algorithm. |
| `patterns/` | [`double_top.py`](metal_analyzer/patterns/double_top.py) | Double Top (M-Top) detection logic using SciPy filters. |
| | [`double_bottom.py`](metal_analyzer/patterns/double_bottom.py) | Double Bottom (W-Bottom) detection logic. |
| `models/` | [`short_trend_predictor.py`](metal_analyzer/models/short_trend_predictor.py) | Short-term trend analysis including RSI divergence & 200EMA support. |
| | [`top_down.py`](metal_analyzer/models/top_down.py) | Multi-timeframe top-down analysis logic. |
| `models/` | [`top_down.py`](metal_analyzer/models/top_down.py) | Top-down alignment logic. |
| `examples/` | [`demo.py`](examples/demo.py) | Comprehensive analysis demo script using the latest market data. |
| | [`demo-20260130.py`](examples/demo-20260130.py) | Simulation script for the Jan 2026 crash scenario. |
| | [`demo-20251230.py`](examples/demo-20251230.py) | Simulation script for the Dec 2025 trend transition scenario. |
