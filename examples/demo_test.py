"""過去の急騰・急落局面における予測精度を検証するスクリプト。

直近3ヶ月（2025/11/01 - 2026/02/04）の価格変動率2.0%以上の全12ケースを検証します。
"""

import yfinance as yf
from metal_analyzer import MetalAnalyzer
import pandas as pd
import datetime
import os

def run_backtest():
    ticker = "GC=F"
    analyzer = MetalAnalyzer(ticker=ticker)
    
    # 検証するシナリオ: (ラベル, ターゲット日付(この日の終わり時点のデータを使う), 翌日の実際の結果)
    test_cases = [
        # 直近3ヶ月の全検証シナリオ (2025/11/01 - 2026/02/04)
        # 変動率 2.0% 以上の全12ケース
        
        # 1. 2026-02-03 (火) 急騰 (+10.33%) -> 前日 02-02
        ("2026/02/03 急騰", "2026-02-02", "翌日 +10.3% 急騰"),
        
        # 2. 2026-01-30 (金) 急落 (-11.37%) -> 前日 01-29
        ("2026/01/30 暴落", "2026-01-29", "翌日 -11.4% 暴落"),
        
        # 3. 2026-01-28 (水) 急騰 (+4.36%) -> 前日 01-27
        ("2026/01/28 急騰", "2026-01-27", "翌日 +4.4% 急騰"),
        
        # 4. 2026-01-26 (月) 急騰 (+2.08%) -> 前週金曜 01-23
        ("2026/01/26 急騰", "2026-01-23", "翌週 +2.1% 急騰"),
        
        # 5. 2026-01-20 (火) 急騰 (+3.73%) -> 前日 01-19
        ("2026/01/20 急騰", "2026-01-19", "翌日 +3.7% 急騰"),
        
        # 6. 2026-01-12 (月) 急騰 (+2.54%) -> 前週金曜 01-09
        ("2026/01/12 急騰", "2026-01-09", "翌週 +2.5% 急騰"),
        
        # 7. 2026-01-05 (月) 急騰 (+2.84%) -> 前週金曜 01-02
        ("2026/01/05 急騰", "2026-01-02", "翌週 +2.8% 急騰"),
        
        # 8. 2025-12-29 (月) 急落 (-4.50%) -> 前週金曜 12-26
        ("2025/12/29 下落", "2025-12-26", "翌週 -4.5% 急落"),
        
        # 9. 2025-12-11 (木) 急騰 (+2.12%) -> 前日 12-10
        ("2025/12/11 急騰", "2025-12-10", "翌日 +2.1% 急騰"),
        
        # 10. 2025-11-14 (金) 急落 (-2.37%) -> 前日 11-13
        ("2025/11/14 急落", "2025-11-13", "翌日 -2.4% 急落"),
        
        # 11. 2025-11-12 (水) 急騰 (+2.38%) -> 前日 11-11
        ("2025/11/12 急騰", "2025-11-11", "翌日 +2.4% 急騰"),
        
        # 12. 2025-11-10 (月) 急騰 (+2.81%) -> 前週金曜 11-07
        ("2025/11/10 急騰", "2025-11-07", "翌週 +2.8% 急騰"),
    ]

    print(f"=== Metal Analyzer 過去検証バックテスト (Ticker: {ticker}) ===\n")

    for label, target_date_str, actual_result in test_cases:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"■ {label} (分析基準日: {target_date_str})")
        print(f"   >> 実際の結果: {actual_result}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        target_dt = pd.to_datetime(target_date_str)
        end_dt = target_dt + pd.Timedelta(days=1)
        end_str = end_dt.strftime('%Y-%m-%d')
        
        start_str = (target_dt - pd.Timedelta(days=730)).strftime('%Y-%m-%d')
        
        d_df = yf.download(ticker, start=start_str, end=end_str, interval="1d", progress=False)
        h1_start_str = (target_dt - pd.Timedelta(days=59)).strftime('%Y-%m-%d')
        h1_df = yf.download(ticker, start=h1_start_str, end=end_str, interval="1h", progress=False)

        if d_df.empty or h1_df.empty:
            print("  [Error] データが取得できませんでした（期間外の可能性があります）。\n")
            continue

        for df in [d_df, h1_df]:
            if isinstance(df.columns, pd.MultiIndex):
                if 'Close' in df.columns.get_level_values(0):
                    df.columns = df.columns.get_level_values(0)
                elif len(df.columns.levels) > 1 and 'Close' in df.columns.get_level_values(1):
                    df.columns = df.columns.get_level_values(1)
            
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)

        if not h1_df.empty:
            h4_df = h1_df.resample('4h').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
        else:
            h4_df = pd.DataFrame()

        analyzer.timeframe_data = {}
        analyzer.add_timeframe_data("Daily", d_df)
        analyzer.add_timeframe_data("1h", h1_df)
        analyzer.add_timeframe_data("4h", h4_df)

        analyzer.analyze_short_trend()
        print("\n")

if __name__ == "__main__":
    run_backtest()
