# Metal Analyzer

A Python library for analyzing precious metal (e.g., Gold) prices, determining trends, and detecting specific chart patterns like Double Tops.

## Features

- **Multi-Timeframe Analysis**: Top-down analysis combining daily and hourly data.
- **Pattern Detection**: Advanced Double Top (M-top) detection using SciPy.
- **Modular Architecture**: Separated modules for `indicators`, `patterns`, and `models`.
- **Decoupled Data Source**: Accepts standard Pandas DataFrames from any sources (e.g., `yfinance`).

## Installation

```bash
cd metal-analyzer
pip install .
```

## Analysis Scenarios and Results

The library includes three demo scripts to showcase its main features.

### 1. Latest Analysis (`examples/demo.py`)
Fetches the most recent market data and analyzes current trends.

#### Sample Code
```python
import yfinance as yf
from metal_analyzer import MetalAnalyzer

ticker = "GC=F"
analyzer = MetalAnalyzer(ticker=ticker)

# Fetching data externally
daily_data = yf.download(ticker, period="1y", interval="1d")
hourly_data = yf.download(ticker, period="1mo", interval="1h")

# Running analysis
analyzer.set_data(daily_data)
analyzer.calculate_sma(20)
analyzer.calculate_rsi(14)
analyzer.set_multi_timeframe_data(daily_data, hourly_data)
analyzer.analyze_top_down()
```

#### Output Example
![Latest Analysis Chart](examples/outputs/demo.png)

---

### 2. Jan 30, 2026 Crash Detection (`examples/demo-20260130.py`)
Simulates the historical price collapse and demonstrates the Sell alert.

#### Execution Result
```text
Result: [ALERT] Double Top detected! Peaks: 5591.00, 5467.60. Sell signal as it broke the neckline at 5212.90.
```

#### Chart Image
![Jan 30 Crash Chart](examples/outputs/demo-20260130.png)

---

### 3. Dec 30, 2025 Simulation (`examples/demo-20251230.py`)
Simulates the "Pattern Forming" state just before a drop (neckline not yet broken).

#### Execution Result
```text
Double Top Result: Pattern forming, but neckline not broken yet (a break below the neckline confirms the trend reversal).
```

#### Chart Image
![Dec 30 Simulation Chart](examples/outputs/demo-20251230.png)

## Project Structure

- `metal_analyzer/core/`: Core `MetalAnalyzer` class.
- `metal_analyzer/indicators/`: SMA, RSI calculations.
- `metal_analyzer/patterns/`: Chart pattern detection (e.g., Double Top).
- `metal_analyzer/models/`: Composite logic (e.g., Top-down analysis).
