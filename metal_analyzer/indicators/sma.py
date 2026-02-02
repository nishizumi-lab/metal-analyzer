import pandas as pd

def calculate_sma(df, window=20):
    """単純移動平均(SMA)を計算する。

    Args:
        df (pd.DataFrame): 'Close' 列を含むデータフレーム。
        window (int): 平均を取る期間。

    Returns:
        pd.Series: SMAの値を持つシリーズ。データが不足している場合はNone。
    """
    if 'Close' not in df.columns:
        return None
    return df['Close'].rolling(window=window).mean()

def calculate_ema(df, window=20):
    """指数平滑移動平均(EMA)を計算する。

    Args:
        df (pd.DataFrame): 'Close' 列を含むデータフレーム。
        window (int): 平均を取る期間。

    Returns:
        pd.Series: EMAの値を持つシリーズ。
    """
    if 'Close' not in df.columns:
        return None
    return df['Close'].ewm(span=window, adjust=False).mean()
