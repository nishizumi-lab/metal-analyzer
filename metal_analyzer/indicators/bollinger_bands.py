"""ボリンジャーバンドの計算を行うモジュール。

このモジュールは、指定された期間と標準偏差に基づいて、
ボリンジャーバンド（ミドル、アッパー、ローワー）を計算する関数を提供します。
"""

import pandas as pd

def calculate_bollinger_bands(df, window=20, num_std=2):
    """ボリンジャーバンドを計算する。

    Args:
        df (pd.DataFrame): 'Close' 列を含むデータフレーム。
        window (int): 移動平均の期間。デフォルトは20。
        num_std (int): 標準偏差の倍数。デフォルトは2。

    Returns:
        tuple: (pd.Series, pd.Series, pd.Series) 
            (ミドルバンド, アッパーバンド, ローワーバンド) のタプル。
            'Close' 列がない場合は (None, None, None) を返します。
    """
    if 'Close' not in df.columns:
        return None, None, None
    
    middle_band = df['Close'].rolling(window=window).mean()
    std_dev = df['Close'].rolling(window=window).std()
    
    upper_band = middle_band + (std_dev * num_std)
    lower_band = middle_band - (std_dev * num_std)
    
    return middle_band, upper_band, lower_band
