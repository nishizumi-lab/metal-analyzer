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

    # 追加の分析セクション
    d_df = analyzer.daily_data
    h1_df = analyzer.hourly_data

    if d_df is not None and h1_df is not None:
        print(f"[3] マルチタイムフレーム分析")
        from metal_analyzer.models import analyze_top_down
        signal, prediction, d_trend, h_trend, h_rsi = analyze_top_down(d_df, h1_df)
        print(f"長期トレンド： {d_trend}")
        print(f"短期トレンド： {h_trend}")
        print(f"短期RSI： {h_rsi:.2f}")
        print(f"判定： {signal}")
        print(f"予測： {prediction}\n")

        print(f"[4] エントリーシグナル判定")
        from metal_analyzer.models import determine_entry_signals
        # 1時間足で判定
        signals = determine_entry_signals(h1_df)
        last_sig = signals.iloc[-1]
        sig_desc = "買い (Buy)" if last_sig == 1 else "売り (Sell)" if last_sig == -1 else "様子見 (Wait)"
        print(f"1時間足シグナル： {sig_desc}\n")

        print(f"[5] チャートパターン検知")
        detected, details = analyzer.detect_double_top()
        status = "検知あり" if detected else "検知なし"
        print(f"ダブルトップ： {status}")
        print(f"詳細： {details}\n")

    print(f"=== 全工程が完了しました ===")
    print(f"チャート出力先: {output_dir}")

if __name__ == "__main__":
    run_multi_timeframe_demo()
