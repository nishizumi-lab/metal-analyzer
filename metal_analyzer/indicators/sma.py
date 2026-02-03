"""移動平均線（SMA, EMA）の計算を行うモジュール。

このモジュールは、指定された期間に基づいて単純移動平均（SMA）および
指数平滑移動平均（EMA）を計算する関数を提供します。
"""

import pandas as pd

def calculate_sma(df, window=20):
    """単純移動平均 (SMA) を計算する。

    Args:
        df (pd.DataFrame): 'Close' 列を含むデータフレーム。
        window (int): 平均を取る期間。デフォルトは20。

    Returns:
        pd.Series or None: SMAの値を持つシリーズ。'Close' 列がない場合は None。
    """
    if 'Close' not in df.columns:
        return None
    return df['Close'].rolling(window=window).mean()

def calculate_ema(df, window=20):
    """指数平滑移動平均 (EMA) を計算する。

    Args:
        df (pd.DataFrame): 'Close' 列を含むデータフレーム。
        window (int): 平均を取る期間。デフォルトは20。

    Returns:
        pd.Series or None: EMAの値を持つシリーズ。'Close' 列がない場合は None。
    """
    if 'Close' not in df.columns:
        return None
    return df['Close'].ewm(span=window, adjust=False).mean()
