
import yfinance as yf
import pandas as pd

def find_recent_moves():
    ticker = "GC=F"
    start_date = "2025-11-01"
    end_date = "2026-02-04"
    
    print(f"Downloading data for {ticker} from {start_date} to {end_date}...")
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # 前日比の計算
    df['Pct_Change'] = df['Close'].pct_change() * 100
    
    # 変動率が2.0%以上（急騰）または-2.0%以下（急落）の日を抽出
    significant_moves = df[abs(df['Pct_Change']) >= 2.0].copy()
    significant_moves['Type'] = significant_moves['Pct_Change'].apply(lambda x: 'Surge (急騰)' if x > 0 else 'Crash (急落)')
    
    # 日付でソート（新しい順）
    significant_moves = significant_moves.sort_index(ascending=False)
    
    print(f"\nFound {len(significant_moves)} significant moves (|Change| >= 2.0%) in the last 3 months:")
    print("-" * 60)
    print(f"{'Date':<12} | {'Close':<10} | {'Change(%)':<10} | {'Type'}")
    print("-" * 60)
    
    for date, row in significant_moves.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        print(f"{date_str:<12} | {row['Close']:.2f}      | {row['Pct_Change']:+.2f}%     | {row['Type']}")
        # 分析基準日（前日）
        prev_day = date - pd.Timedelta(days=1)
        # 簡易的に前日を表示（実際は営業日考慮が必要だが目安として）
        # print(f"  Target Date: {prev_day.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    find_recent_moves()
