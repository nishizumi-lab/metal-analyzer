import yfinance as yf
import os
from metal_analyzer import MetalAnalyzer

def run_latest_analysis():
    """最新の市場データを用いた総合分析デモ。

    プロセス：
    1. yfinanceを用いたデータの外部取得。
    2. テクニカル指標（SMA, RSI）の計算。
    3. トップダウン分析（週足・日足等）の実行。
    4. 結果のチャート画像保存。
    """
    print("=== Metal Analyzer 最新分析デモ ===")
    
    ticker = "GC=F"
    analyzer = MetalAnalyzer(ticker=ticker)

    # 1. データの外部取得
    print(f"\n[1] データ取得中: {ticker}")
    daily_data = yf.download(ticker, period="1y", interval="1d")
    hourly_data = yf.download(ticker, period="1mo", interval="1h")

    if daily_data.empty or hourly_data.empty:
        print("データの取得に失敗しました。")
        return

    # 2. 基本的なテクニカル分析
    print("\n[2] テクニカル指標の計算中...")
    analyzer.set_data(daily_data)
    analyzer.calculate_sma(window=20)
    analyzer.calculate_sma(window=50)
    analyzer.calculate_rsi(window=14)
    analyzer.analyze_entry_points()
    
    latest_date = analyzer.data.index[-1].strftime('%Y-%m-%d')
    print(f"最新データ日: {latest_date}")
    print(f"最新のRSI: {analyzer.data['RSI'].iloc[-1]:.2f}")

    # 3. トップダウン分析
    print("\n[3] トップダウン分析を実行中...")
    analyzer.set_multi_timeframe_data(daily_data, hourly_data)
    analyzer.analyze_top_down()

    # 4. グラフの保存
    output_dir = os.path.join("examples", "outputs")
    output_file = os.path.join(output_dir, "demo.png")
    print(f"\n[4] グラフを保存中: {output_file}")
    
    analyzer.plot_data(filename=output_file)

    print(f"\n=== 完了: 結果は {output_file} に保存されました ===")

if __name__ == "__main__":
    run_latest_analysis()
