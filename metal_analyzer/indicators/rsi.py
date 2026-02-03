"""相対力指数 (RSI) の計算を行うモジュール。

このモジュールは、指定された期間に基づいて市場の売られすぎ・買われすぎを
判断するためのRSIを計算する関数を提供します。
"""

import pandas as pd

def calculate_rsi(df, window=14):
    """RSI (Relative Strength Index) を計算する。

    Args:
        df (pd.DataFrame): 'Close' 列を含むデータフレーム。
        window (int): 計算期間。デフォルトは14。

    Returns:
        pd.Series or None: RSIの値を持つシリーズ。'Close' 列がない場合は None。
    """
    if 'Close' not in df.columns:
        return None
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    # ゼロ除算を避けるために rs が None にならないよう配慮が必要な場合もあるが、
    # 通常は pandas の演算で NaN が適切に処理される。
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
