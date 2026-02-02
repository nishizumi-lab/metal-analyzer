import yfinance as yf
import os
from metal_analyzer import MetalAnalyzer

def run_simulation_20251230():
    """2025年12月30日の暴落直前の状況を再現するデモ。

    プロセス：
    1. yfinanceを用いたデータの過去取得。
    2. 暴落直前（2025-12-30 10:00）までのデータにフィルタリング。
    3. ロジックの実行。
    4. 結果のチャート画像保存。
    """
    print("=== Metal Analyzer シミュレーション (2025/12/30 暴落直前) ===")
    
    ticker = "GC=F"
    analyzer = MetalAnalyzer(ticker=ticker)

    # 1. データの取得
    print(f"\n[1] 過去データを取得中...")
    # 期間を広めに確保
    daily_data = yf.download(ticker, start="2025-01-01", end="2026-01-05", interval="1d")
    hourly_data = yf.download(ticker, start="2025-11-01", end="2026-01-05", interval="1h")

    # 2. 暴落直前までのデータにフィルタリング
    # 12/30の急落を捉えるための時点
    target_time = '2025-12-30 10:00:00'
    sim_hourly = hourly_data[hourly_data.index <= target_time]
    sim_daily = daily_data[daily_data.index <= target_time]

    if sim_hourly.empty or len(sim_hourly) < 100:
        print("指定された日時のデータが取得期間内に不足しています。")
        return

    # 3. 分析の実行
    print(f"\n[2] シミュレーション時間: {target_time}")
    analyzer.set_multi_timeframe_data(sim_daily, sim_hourly)
    
    print("\n--- その時点での判定 ---")
    analyzer.analyze_top_down()
    
    detected, details = analyzer.detect_double_top(threshold=0.03, lookback=100)
    print(f"ダブルトップ判定: {details}")

    # 4. グラフの保存
    analyzer.set_data(sim_hourly.tail(200))
    analyzer.calculate_sma(20)
    analyzer.calculate_rsi(14)
    
    output_dir = os.path.join("examples", "outputs")
    output_file = os.path.join(output_dir, "demo-20251230.png")
    print(f"\n[3] グラフを保存中: {output_file}")
    
    analyzer.plot_data(filename=output_file)

    print(f"\n=== シミュレーション完了 ===")

if __name__ == "__main__":
    run_simulation_20251230()
