"""チャートパターン検知を行うモジュール（ダブルボトム）。

このモジュールは、SciPyを使用して価格データからダブルボトム（Wボトム）を
自動的に検知する機能を提供します。
"""

import numpy as np
from scipy.signal import find_peaks

def detect_double_bottom(hourly_data, threshold=0.03, lookback=100):
    """ダブルボトム（Wボトム）パターンを検知し、ネックライン上抜けで買いシグナルを判定する。

    価格データから2つの谷を探し、その深さが一定の範囲内であること、および
    現在価格がその間の山（ネックライン）を上回っているかを確認します。

    Args:
        hourly_data (pd.DataFrame): 1時間足などの価格データ。'Close' 列が必要。
        threshold (float): 2つの谷の価格差の許容割合。デフォルト 0.03 (3%)。
        lookback (int): 分析対象とする過去のデータ数。デフォルト 100。

    Returns:
        tuple: (is_detected, signal_details)
            is_detected (bool): パターンが成立し、買い条件を満たしているか。
            signal_details (str): 検知結果の詳細メッセージ（日本語）。
    """
    if hourly_data is None or hourly_data.empty:
         return False, "分析対象のデータがありません"

    # 分析対象データの取得（直近 lookback 期間）
    df = hourly_data.iloc[-lookback:].copy()
    
    # 谷を検出するために価格を反転させる（find_peaksは山を探すため）
    prices = df['Close'].values
    inverted_prices = -prices

    # ピーク（谷）の検出
    peaks, properties = find_peaks(inverted_prices, distance=10, prominence=5) 
    
    if len(peaks) < 2:
        return False, "谷が不足しています。"
        
    last_peak_idx = peaks[-1]
    second_last_peak_idx = peaks[-2]
    
    # 谷の価格（元の価格に戻すにはマイナスを掛ける）
    valley1_price = prices[second_last_peak_idx]
    valley2_price = prices[last_peak_idx]
    
    diff_ratio = abs(valley1_price - valley2_price) / valley1_price
    
    if diff_ratio > threshold:
        return False, f"谷の価格差が大きすぎます: {diff_ratio:.2%}。"
        
    # 間の山（ネックライン）を探す
    # 2つの谷の間にある最高値
    peak_rel_idx = np.argmax(prices[second_last_peak_idx:last_peak_idx])
    peak_idx = second_last_peak_idx + peak_rel_idx
    neckline_price = prices[peak_idx]
    
    current_price = hourly_data['Close'].iloc[-1]
    
    if current_price > neckline_price:
         return True, f"ダブルボトムを検知しました！ 谷: {valley1_price:.2f}, {valley2_price:.2f}. ネックライン {neckline_price:.2f} を上抜けたため、買いシグナルです。"
    
    return False, f"Wボトム形成中ですが、ネックラインを上抜けていません。ネックライン: {neckline_price:.2f}, 現在値: {current_price:.2f}"
