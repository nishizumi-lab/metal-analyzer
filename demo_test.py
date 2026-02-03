"""過去の急騰・急落局面における予測精度を検証するスクリプト。

ここ数ヶ月で価格変動が大きかった以下のタイミングを検証します：
1. 2025-10-21 (5.7% 下落) の前日 -> 暴落予兆があったか？
2. 2025-12-29 (4.5% 下落) の前日 -> トレンド転換を示唆していたか？
3. 2026-01-30 (11% 大暴落) の前日 -> 大暴落シグナル（またはその予兆）が出ていたか？
4. 2026-02-03 (6.9% 急騰) の前日 -> 反発の兆しを検知できていたか？
"""

import yfinance as yf
from metal_analyzer import MetalAnalyzer
import pandas as pd
import datetime

def run_backtest():
    ticker = "GC=F"
    analyzer = MetalAnalyzer(ticker=ticker)
    
    # 検証するシナリオ: (ラベル, ターゲット日付(この日の終わり時点のデータを使う), 翌日の実際の結果)
    test_cases = [
        ("2025年10月 急落前夜", "2025-10-20", "翌日 -5.7% 急落"),
        ("2025年12月 下落前夜", "2025-12-26", "翌週 -4.5% 下落"), # 29は月曜なので金曜26日時点
        ("2026年1月 大暴落前夜", "2026-01-29", "翌日 -11.3% 大暴落"),
        ("2026年2月 急騰前夜",   "2026-02-02", "翌日 +6.9% 急騰"),
    ]

    print(f"=== Metal Analyzer 過去検証バックテスト (Ticker: {ticker}) ===\n")

    for label, target_date_str, actual_result in test_cases:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"■ {label} (分析基準日: {target_date_str})")
        print(f"   >> 実際の結果: {actual_result}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # データの取得終了日（翌日を指定しないと当日の日足が含まれないことがあるため+1日などを考慮）
        # yfinanceのendはexcludeなので、target_dateの翌日を指定してtarget_dateまでを含める
        target_dt = pd.to_datetime(target_date_str)
        end_dt = target_dt + pd.Timedelta(days=1)
        end_str = end_dt.strftime('%Y-%m-%d')
        
        # データ取得 (日足、4時間足、1時間足)
        # 十分な過去データを含むようにstartを設定
        start_str = (target_dt - pd.Timedelta(days=730)).strftime('%Y-%m-%d')
        
        d_df = yf.download(ticker, start=start_str, end=end_str, interval="1d", progress=False)
        h1_df = yf.download(ticker, start=(target_dt - pd.Timedelta(days=59)).strftime('%Y-%m-%d'), end=end_str, interval="1h", progress=False)

        if d_df.empty or h1_df.empty:
            print("  [Error] データが取得できませんでした。\n")
            continue

        # yfinanceのMultiIndex対応 (Resample前にフラット化が必要)
        for df in [d_df, h1_df]:
            if isinstance(df.columns, pd.MultiIndex):
                # 'Close'が含まれるレベルを探して採用する
                if 'Close' in df.columns.get_level_values(0):
                    df.columns = df.columns.get_level_values(0)
                elif len(df.columns.levels) > 1 and 'Close' in df.columns.get_level_values(1):
                    df.columns = df.columns.get_level_values(1)

        # 4時間足は1時間足から生成
        h4_df = h1_df.resample('4h').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna()

        # Analyzerにセット
        analyzer.add_timeframe_data("Daily", d_df)
        analyzer.add_timeframe_data("1h", h1_df)
        analyzer.add_timeframe_data("4h", h4_df)

        # 分析実行
        # コンソール出力は `analyze_advanced_trend` が行うため、ここでは呼び出すだけ
        analyzer.analyze_advanced_trend()
        print("\n")

if __name__ == "__main__":
    run_backtest()
