
import yfinance as yf
import pandas as pd

def find_significant_moves():
    ticker = "GC=F"
    # 現在が2026年2月なので、過去1年半くらいを取得
    end_date = "2026-02-04"
    start_date = "2024-01-01"
    
    print(f"Downloading data for {ticker} from {start_date} to {end_date}...")
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # 前日比の計算
    df['Pct_Change'] = df['Close'].pct_change() * 100
    
    # 変動率が2.5%以上（急騰）または-2.5%以下（急落）の日を抽出
    significant_moves = df[abs(df['Pct_Change']) >= 2.5].copy()
    significant_moves['Type'] = significant_moves['Pct_Change'].apply(lambda x: 'Surge (急騰)' if x > 0 else 'Crash (急落)')
    
    # 日付でソート（新しい順）
    significant_moves = significant_moves.sort_index(ascending=False)
    
    print(f"\nFound {len(significant_moves)} significant moves (|Change| >= 2.5%):")
    print("-" * 60)
    print(f"{'Date':<12} | {'Close':<10} | {'Change(%)':<10} | {'Type'}")
    print("-" * 60)
    
    for date, row in significant_moves.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        print(f"{date_str:<12} | {row['Close']:.2f}      | {row['Pct_Change']:+.2f}%     | {row['Type']}")
        # 分析基準日は「前日」にする必要があるため、前日も表示しておくと便利
        prev_day = date - pd.Timedelta(days=1)
        # 土日を考慮して、データが存在する直近の営業日を探すのはdemo_test.pyの役割だが、
        # ここでは単純にカレンダー上の前日を表示
        # print(f"  Target Date for Analysis: {prev_day.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    find_significant_moves()
