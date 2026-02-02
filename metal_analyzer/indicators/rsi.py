import pandas as pd

def calculate_rsi(df, window=14):
    """RSI (Relative Strength Index) を計算する。

    Args:
        df (pd.DataFrame): 'Close' 列を含むデータフレーム。
        window (int): 計算期間。

    Returns:
        pd.Series: RSIの値を持つシリーズ。データが不足している場合はNone。
    """
    if 'Close' not in df.columns:
        return None
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
