import pandas as pd

def determine_entry_signals(df):
    """SMAクロスとRSIに基づいて売買シグナルを判定する。

    Args:
        df (pd.DataFrame): 'SMA_20', 'SMA_50', 'RSI' を含むデータフレーム。

    Returns:
        pd.Series: 判定シグナル (-1: 売り, 0: 様子見, 1: 買い)。
    """
    signals = pd.Series(0, index=df.index)
    
    # SMAクロス判定
    if 'SMA_20' in df.columns and 'SMA_50' in df.columns:
        prev_sma20 = df['SMA_20'].shift(1)
        prev_sma50 = df['SMA_50'].shift(1)
        
        # ゴールデンクロス
        golden_cross = (prev_sma20 < prev_sma50) & (df['SMA_20'] > df['SMA_50'])
        signals.loc[golden_cross] = 1
        
        # デッドクロス
        dead_cross = (prev_sma20 > prev_sma50) & (df['SMA_20'] < df['SMA_50'])
        signals.loc[dead_cross] = -1
        
    # RSIシグナル (判定がない場合のみ)
    if 'RSI' in df.columns:
        # 売られすぎ (Buy)
        rsi_buy = (df['RSI'] < 30) & (signals == 0)
        signals.loc[rsi_buy] = 1
        
        # 買われすぎ (Sell)
        rsi_sell = (df['RSI'] > 70) & (signals == 0)
        signals.loc[rsi_sell] = -1
        
    return signals
