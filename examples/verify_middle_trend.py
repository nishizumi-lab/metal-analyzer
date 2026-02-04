"""中期トレンド分析機能の検証スクリプト。

Yahoo Financeから最新のゴールドデータ（週足・日足）を取得し、
`metal_analyzer.models.middle_trend_predictor` の動作をテストします。
"""
import yfinance as yf
import pandas as pd
import sys
import os

# プロジェクトルートをパスに追加してモジュールをインポート可能にする
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metal_analyzer.models.middle_trend_predictor import analyze_middle_trend

def verify_middle_trend():
    print("=== 中期トレンド分析 (Middle Trend Predictor) 検証 ===")
    ticker = "GC=F"
    
    # データの取得
    print(f"データ取得中 ({ticker})...")
    # 週足: 過去2年 (EMA52計算用)
    weekly_data = yf.download(ticker, period="2y", interval="1wk", progress=False)
    # 日足: 過去1年
    daily_data = yf.download(ticker, period="1y", interval="1d", progress=False)
    
    if weekly_data.empty or daily_data.empty:
        print("データ取得に失敗しました。")
        return

    print("分析実行中...")
    results = analyze_middle_trend(weekly_data, daily_data)
    
    print("\n--- 分析結果 ---")
    print(f"週足構造 (Deep Snow): {results['dashboard_1_weekly']}")
    print(f"日足モメンタム (Surface Alert): {results['dashboard_2_daily']}")
    print(f"ボラティリティ (Warsh Mode): {results['dashboard_3_volatility']}")
    print(f"戦略 (Deep Dip): {results['dashboard_4_strategy']}")
    print(f"\n総合コメント:\n{results['final_prediction']}")
    print("----------------")

if __name__ == "__main__":
    verify_middle_trend()
