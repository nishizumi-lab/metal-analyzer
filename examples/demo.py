"""最新の市場データを使用した総合的な分析デモスクリプト。

このスクリプトは、Yahoo Financeから最新のゴールド価格データを取得し、
全時間足（月・週・日・1時・15分）のチャート生成と高度トレンド予測を実行します。
"""

import yfinance as yf
import os
import pandas as pd
from metal_analyzer import MetalAnalyzer

def run_multi_timeframe_demo():
    """最新データに基づいた全時間足チャートと高度分析デモを実行する。"""
    print("=== Metal Analyzer 総合分析デモ ===")
    
    ticker = "GC=F"
    analyzer = MetalAnalyzer(ticker=ticker)
    output_dir = os.path.join("examples", "outputs", "candles")
    
    timeframes = [
        ("Monthly", "1mo", "15y"),
        ("Weekly", "1wk", "5y"),
        ("Daily", "1d", "2y"),
        ("1h", "1h", "2mo"),
        ("15m", "15m", "1mo"),
    ]

    print(f"\n[1] データ取得およびチャート生成中...")
    for name, interval, period in timeframes:
        print(f"--- {name} ({interval}) を処理中 ---")
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty: continue
        analyzer.add_timeframe_data(name, data)
        analyzer.plot_candlestick(name, filename=os.path.join(output_dir, f"chart_{name.lower()}.png"))

    print(f"\n[2] 高度なトレンド分析")
    analyzer.analyze_advanced_trend()

    print(f"\n=== 全工程が完了しました ===")
    print(f"チャート出力先: {output_dir}")

if __name__ == "__main__":
    run_multi_timeframe_demo()
