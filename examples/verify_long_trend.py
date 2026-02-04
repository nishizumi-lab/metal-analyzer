"""長期トレンド分析機能の検証スクリプト。

Yahoo Financeから最新のデータ（金、銀、プラチナ、DXY、TIPS）を取得し、
`metal_analyzer.models.long_trend_predictor` の動作をテストします。
"""
import yfinance as yf
import pandas as pd
import sys
import os

# プロジェクトルートをパスに追加してモジュールをインポート可能にする
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metal_analyzer.models.long_trend_predictor import analyze_long_trend

def verify_long_trend():
    print("=== 長期トレンド分析 (Long Trend Predictor) 検証 ===")
    
    # データの取得
    print("データ取得中...")
    # 金、銀、プラチナ、ドルインデックス (DXY)、TIPS ETF
    tickers = {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Platinum": "PL=F",
        "DXY": "DX-Y.NYB",
        "TIPS": "TIP"
    }
    
    data = {}
    for name, ticker in tickers.items():
        print(f"  {name} ({ticker})")
        # 月足: 過去10年
        df = yf.download(ticker, period="10y", interval="1mo", progress=False)
        if hasattr(df.columns, 'droplevel'): # MultiIndex対策
             df.columns = df.columns.get_level_values(0) if isinstance(df.columns, pd.MultiIndex) else df.columns
        data[name] = df

    print("分析実行中...")
    results = analyze_long_trend(
        data['Gold'],
        data['Silver'],
        data['Platinum'],
        data['DXY'],
        data['TIPS']
    )
    
    print("\n--- 分析結果 ---")
    print(f"ダッシュボード1 (通貨価値): {results['dashboard_1_currency']}")
    print(f"ダッシュボード2 (相対価値): {results['dashboard_2_ratio']}")
    print(f"ダッシュボード3 (マクロ環境): {results['dashboard_3_macro']}")
    print(f"ダッシュボード4 (ポートフォリオ): {results['dashboard_4_portfolio']}")
    print(f"\n総合コメント:\n{results['final_prediction']}")
    print("----------------")

if __name__ == "__main__":
    verify_long_trend()
