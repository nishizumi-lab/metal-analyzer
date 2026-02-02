import yfinance as yf
import os
import pandas as pd
from metal_analyzer import MetalAnalyzer

def run_simulation(tag, end_time, title_suffix):
    """汎用シミュレーション実行器。"""
    print(f"\n{'='*60}\n シミュレーション: {title_suffix} ({end_time})\n{'='*60}")
    
    ticker = "GC=F"
    analyzer = MetalAnalyzer(ticker=ticker)
    
    configs = [
        ("Monthly", "1mo", 365*10),
        ("Weekly", "1wk", 365*5),
        ("Daily", "1d", 365*2),
        ("1h", "1h", 60),
        ("15m", "15m", 15)
    ]
    
    for name, interval, days in configs:
        start = (pd.to_datetime(end_time) - pd.Timedelta(days=days)).strftime('%Y-%m-%d')
        data = yf.download(ticker, start=start, end="2026-02-05", interval=interval)
        if not data.empty:
            sim_data = data[data.index <= end_time]
            analyzer.add_timeframe_data(name, sim_data)
    
    analyzer.analyze_all(prefix=f"{tag}_")

if __name__ == "__main__":
    run_simulation("20251230", "2025-12-30 10:00:00", "レンジから上昇局面・分析")
