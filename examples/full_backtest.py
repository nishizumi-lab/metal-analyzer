
import yfinance as yf
from metal_analyzer import MetalAnalyzer
import pandas as pd
import datetime
import os

def run_full_period_backtest():
    ticker = "GC=F"
    start_date = "2025-11-01"
    end_date = "2026-02-04"
    
    print(f"=== Metal Analyzer Full Period Backtest (Ticker: {ticker}) ===")
    print(f"Period: {start_date} to {end_date}\n")
    
    # 1. 元データの取得 (期間全体 + 過去分)
    data_start = (pd.to_datetime(start_date) - pd.Timedelta(days=730)).strftime('%Y-%m-%d')
    # yfinance end is exclusive, but we want up to end_date. daily data includes end_date if we request end_date + 1
    fetch_end = (pd.to_datetime(end_date) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    
    print("Downloading data...")
    d_df_all = yf.download(ticker, start=data_start, end=fetch_end, interval="1d", progress=False)
    
    # Clean up MultiIndex
    if isinstance(d_df_all.columns, pd.MultiIndex):
         d_df_all.columns = d_df_all.columns.get_level_values(0)

    # タイムゾーン削除 (tz-naiveにする)
    if d_df_all.index.tz is not None:
        d_df_all.index = d_df_all.index.tz_localize(None)
    
    # 1時間足も取得
    # 730日制限があるため、検証期間に必要な分（+200本程度のバッファ）だけ取得する
    # 2025-01-01からなら十分 (検証開始は2025-11-01)
    h1_start_safe = "2025-01-01"
    h1_df_all = yf.download(ticker, start=h1_start_safe, end=fetch_end, interval="1h", progress=False)
    if isinstance(h1_df_all.columns, pd.MultiIndex):
         h1_df_all.columns = h1_df_all.columns.get_level_values(0)

    # タイムゾーン削除
    if h1_df_all.index.tz is not None:
        h1_df_all.index = h1_df_all.index.tz_localize(None)
         
    # ターゲット期間の日付リストを作成
    # 2025-11-01 以降の日付
    target_dates = d_df_all.index[d_df_all.index >= pd.to_datetime(start_date)]
    # ただし、翌日のデータが存在しないと検証できないため、最後の日付は除外する可能性
    
    results = []
    
    analyzer = MetalAnalyzer(ticker=ticker)

    print(f"\nTesting {len(target_dates)} trading days...\n")
    print(f"{'Date':<12} | {'Actual Next Day':<20} | {'Prediction':<30} | {'Result'}")
    print("-" * 85)

    success_count = 0
    total_count = 0

    for i, target_day in enumerate(target_dates):
        target_day_str = target_day.strftime('%Y-%m-%d')
        
        # 翌日のデータを探す
        # target_datesは全取引日とは限らない（ダウンロードデータ依存）
        # d_df_all 全体から探す
        try:
            current_day_idx = d_df_all.index.get_loc(target_day)
            if current_day_idx == len(d_df_all) - 1:
                # 翌日データなし
                continue
                
            next_day_row = d_df_all.iloc[current_day_idx + 1]
            next_day_pct = (next_day_row['Close'] - d_df_all.iloc[current_day_idx]['Close']) / d_df_all.iloc[current_day_idx]['Close'] * 100
        except Exception as e:
            # エラーやデータ不足
            continue

        # Analyzer用のデータをスライス (当日まで)
        # 日足: simple logic, slice up to target_day
        d_slice = d_df_all.loc[:target_day].copy()
        
        # 1時間足: target_dayの引け時刻まで
        # target_day is 00:00:00. We need data up to the Close of target_day?
        # yfinance daily index is 00:00:00. Daily Close is available.
        # So we need hourly data up to end of target_day.
        # target_day + 1 day roughly.
        slice_end_ts = target_day + pd.Timedelta(days=1)
        h1_slice = h1_df_all.loc[:slice_end_ts - pd.Timedelta(seconds=1)].copy() 
        
        if len(d_slice) < 50 or len(h1_slice) < 50:
             continue
             
        # 4時間足生成
        h4_slice = h1_slice.resample('4h').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna()

        # 分析実行
        analyzer.timeframe_data = {}
        analyzer.add_timeframe_data("Daily", d_slice)
        analyzer.add_timeframe_data("1h", h1_slice)
        analyzer.add_timeframe_data("4h", h4_slice)
        
        try:
            res = analyzer.analyze_short_trend()
            pred = res['final_prediction']
            score = res.get('total_score', 0) # total_scoreが返るようにanalyze_short_trend修正必要かも？いやresultsには入ってないか？
            # short_trend_predictor.pyを確認すると results dictionaryには dashboard resultが入ってる
            # final_prediction文字列である程度判断
        except Exception as e:
            pred = "Error"

        # 判定ロジック
        judgement = "Unknown"
        is_success = False
        
        # 実際の結果分類
        actual_desc = ""
        if next_day_pct >= 2.0:
            actual_desc = f"+{next_day_pct:.1f}% (Surge)"
            # 正解: 急騰、反発、底堅い
            if "Surge" in pred or "反発" in pred or "底堅い" in pred:
                judgement = "⭕ Success"
                is_success = True
            elif "Wait" in pred or "様子見" in pred:
                 judgement = "⚠️ Missed (Neutral)" # ニュートラルは部分的な失敗
            else:
                 judgement = "❌ Fail (Wrong Dir)"
                 
        elif next_day_pct <= -2.0:
            actual_desc = f"{next_day_pct:.1f}% (Crash)"
             # 正解: 暴落、続落、下落
            if "Crash" in pred or "続落" in pred or "下落" in pred or "注意" in pred:
                judgement = "⭕ Success"
                is_success = True
            elif "Wait" in pred or "様子見" in pred:
                 judgement = "⚠️ Missed (Neutral)"
            else:
                 judgement = "❌ Fail (Wrong Dir)"
                 
        else:
            actual_desc = f"{next_day_pct:.1f}% (Range)"
            # 正解: 様子見、レンジ
            # 許容: 弱い反発・弱い続落は許容範囲とする（トレンド継続中など）
            # 失敗: 「大暴落加速」「急騰加速」などの強いシグナルが出たのに動かなかった場合（ダマシ）
            
            if "Acceleration" in pred or "大暴落" in pred or "急騰" in pred:
                 judgement = "❌ Fail (False Alarm)"
            else:
                 judgement = "⭕ Success (Quiet)"
                 is_success = True

        print(f"{target_day_str:<12} | {actual_desc:<20} | {pred:<30} | {judgement}")
        
        total_count += 1
        if is_success:
            success_count += 1
            
    print("-" * 85)
    if total_count > 0:
        rate = (success_count / total_count) * 100
        print(f"Total Prediction Accuracy: {rate:.1f}% ({success_count}/{total_count})")
    else:
        print("No validation days found.")

if __name__ == "__main__":
    run_full_period_backtest()
