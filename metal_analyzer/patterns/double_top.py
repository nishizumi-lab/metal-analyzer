"""チャートパターン検知を行うモジュール。

このモジュールは、SciPyを使用して価格データから特定の形状（ダブルトップなど）を
自動的に検知する機能を提供します。
"""

import numpy as np
from scipy.signal import find_peaks

def detect_double_top(hourly_data, threshold=0.03, lookback=100):
    """ダブルトップ（Mトップ）パターンを検知し、ネックライン割れで売りシグナルを判定する。

    価格データから2つの山を探し、その高さが一定の範囲内であること、および
    現在価格がその間の谷（ネックライン）を下回っているかを確認します。

    Args:
        hourly_data (pd.DataFrame): 1時間足などの価格データ。'Close' 列が必要。
        threshold (float): 2つの頂点の価格差の許容割合。デフォルト 0.03 (3%)。
        lookback (int): 分析対象とする過去のデータ数。デフォルト 100。

    Returns:
        tuple: (is_detected, signal_details)
            is_detected (bool): パターンが成立し、売り条件を満たしているか。
            signal_details (str): 検知結果の詳細メッセージ（日本語）。
    """
    if hourly_data is None or hourly_data.empty:
         return False, "分析対象のデータがありません"

    # 分析対象データの取得（直近 lookback 期間）
    df = hourly_data.iloc[-lookback:].copy()
    
    prices = df['Close'].values

    # トレンドの判定（lookback期間の開始時と現在を比較）
    start_price = prices[0]
    current_price = hourly_data['Close'].iloc[-1]
    change_rate = (current_price - start_price) / start_price

    if change_rate >= 0.01:
        trend_desc = "現在は上昇トレンドにあります。"
    elif change_rate <= -0.01:
        trend_desc = "現在は下落トレンドにあります。"
    else:
        trend_desc = "現在は横ばい（レンジ）トレンドにあります。"
    
    # ピーク（極大値）の検出
    peaks, properties = find_peaks(prices, distance=10, prominence=5) 
    
    if len(peaks) < 2:
        return False, f"ピークが不足しています。{trend_desc}"
        
    last_peak_idx = peaks[-1]
    second_last_peak_idx = peaks[-2]
    
    peak1_price = prices[second_last_peak_idx]
    peak2_price = prices[last_peak_idx]
    
    diff_ratio = abs(peak1_price - peak2_price) / peak1_price
    
    if diff_ratio > threshold:
        return False, f"ピークの価格差が大きすぎます: {diff_ratio:.2%}。{trend_desc}"
        
    trough_rel_idx = np.argmin(prices[second_last_peak_idx:last_peak_idx])
    trough_idx = second_last_peak_idx + trough_rel_idx
    neckline_price = prices[trough_idx]
    
    if current_price < neckline_price:
         return True, f"ダブルトップを検知しました！ ピーク: {peak1_price:.2f}, {peak2_price:.2f}. ネックライン {neckline_price:.2f} を下回ったため、売りシグナルです。"
    
    return False, f"パターン形成中ですが、ネックラインを割り込んでいません。ネックライン: {neckline_price:.2f}, 現在値: {current_price:.2f}"
