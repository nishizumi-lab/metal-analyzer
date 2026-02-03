"""歴史的な暴落局面を再現するシミュレーションスクリプト。

2026年1月30日のゴールド大暴落局面を再現し、高度予測エンジンが
「大暴落加速」シグナルを正しく検知できるかを確認します。
"""

import yfinance as yf
import os
import pandas as pd
from metal_analyzer import MetalAnalyzer

def run_simulation(tag, end_time, title_suffix):
    """汎用シミュレーション実行器。

    Args:
        tag (str): 出力ファイルに使用する識別タグ。
        end_time (str): 分析を終了する時間。
        title_suffix (str): 出力時のタイトル。
    """
    print(f"\n{'='*60}\n シミュレーション: {title_suffix} ({end_time})\n{'='*60}")
    
    ticker = "GC=F"
    analyzer = MetalAnalyzer(ticker=ticker)
    
    # 取得する時間足と期間
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
    run_simulation("20260130", "2026-01-30 10:00:00", "最重要局面・分析")
