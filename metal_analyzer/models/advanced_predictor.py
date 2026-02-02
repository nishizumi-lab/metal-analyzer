import pandas as pd
import numpy as np
from ..indicators.sma import calculate_ema, calculate_sma
from ..indicators.rsi import calculate_rsi

def analyze_advanced_trend(daily_df, h4_df, h1_df, patterns=None):
    """高度な4つのダッシュボード指標に基づいた高精度トレンド予測を行う。

    Args:
        daily_df (pd.DataFrame): 日足データ。
        h4_df (pd.DataFrame): 4時間足データ。
        h1_df (pd.DataFrame): 1時間足データ。
        patterns (dict, optional): 検知されたパターン情報。

    Returns:
        dict: 各ダッシュボードの判定結果と最終予測。
    """
    results = {
        'dashboard_1_trend': '不明',
        'dashboard_2_momentum': '不明',
        'dashboard_3_volatility': '不明',
        'dashboard_4_sentiment': '不明',
        'final_prediction': '様子見',
        'risk_level': '中',
        'comment': ''
    }

    if daily_df.empty or h4_df.empty or h1_df.empty:
        results['comment'] = "十分なデータがありません。"
        return results

    # --- Dashboard 1: 長期トレンド (D1/H4 EMA Perfect Order) ---
    h4_ema20 = calculate_ema(h4_df, 20).iloc[-1]
    h4_ema50 = calculate_ema(h4_df, 50).iloc[-1]
    h4_ema200 = calculate_ema(h4_df, 200).iloc[-1]
    h4_close = h4_df['Close'].iloc[-1]

    if h4_close < h4_ema20 < h4_ema50 < h4_ema200:
        results['dashboard_1_trend'] = 'パーフェクトオーダー (強気下降)'
    elif h4_close > h4_ema20 > h4_ema50 > h4_ema200:
        results['dashboard_1_trend'] = 'パーフェクトオーダー (強気上昇)'
    else:
        results['dashboard_1_trend'] = 'トレンド転換点/混在'

    # --- Dashboard 2: モメンタム (H1 EMA 20乖離) ---
    h1_ema20 = calculate_ema(h1_df, 20).iloc[-1]
    h1_close = h1_df['Close'].iloc[-1]
    dist_ema20 = (h1_close - h1_ema20) / h1_ema20
    
    if dist_ema20 < -0.005:
        results['dashboard_2_momentum'] = '下落の勢い強い'
    elif dist_ema20 > 0.005:
        results['dashboard_2_momentum'] = '上昇の勢い強い'
    else:
        results['dashboard_2_momentum'] = '穏やか'

    # --- Dashboard 3: ボラティリティ加速 (ATR/Range Acceleration) ---
    recent_range = (h1_df['High'] - h1_df['Low']).tail(3).mean()
    avg_range = (h1_df['High'] - h1_df['Low']).tail(20).mean()
    
    if recent_range > avg_range * 1.5:
        results['dashboard_3_volatility'] = 'ブレイクアウト/加速中'
        accel_factor = 1.5
    else:
        results['dashboard_3_volatility'] = '安定'
        accel_factor = 1.0

    # --- Dashboard 4: 重要ラインとパターンセンチメント ---
    h1_low_50 = h1_df['Low'].tail(50).min()
    h1_high_50 = h1_df['High'].tail(50).max()
    
    pattern_risk = 0
    if patterns and patterns.get('double_top'):
        neckline = patterns.get('neckline', 0)
        if h1_close < neckline:
            results['dashboard_4_sentiment'] = '重要ライン割れ (暴落確定)'
            pattern_risk = -5
        else:
            results['dashboard_4_sentiment'] = '重要ラインでの攻防'
    else:
        if h1_close <= h1_low_50:
            results['dashboard_4_sentiment'] = '新安値更新'
            pattern_risk = -2
        elif h1_close >= h1_high_50:
            results['dashboard_4_sentiment'] = '新高値更新'
            pattern_risk = 2
        else:
            results['dashboard_4_sentiment'] = 'レンジ内'

    # --- スコアリング ---
    score = 0
    if '下降' in results['dashboard_1_trend']: score -= 3
    if '上昇' in results['dashboard_1_trend']: score += 3
    if '下落' in results['dashboard_2_momentum']: score -= 1
    if '上昇' in results['dashboard_2_momentum']: score += 1
    
    score = (score + pattern_risk) * accel_factor

    if score <= -6:
        results['final_prediction'] = '⚠️ 大暴落加速 (Great Crash Acceleration)'
        results['risk_level'] = '極めて高い'
        results['comment'] = "重要ラインを割り込み、ボラティリティが急増しています。トレンドの底が見えません。"
    elif score >= 6:
        results['final_prediction'] = '🚀 急騰加速 (Surge Acceleration)'
        results['risk_level'] = '高い'
        results['comment'] = "レジスタンスを突破し、強い上昇モメンタムが発生しています。"
    elif score < 0:
        results['final_prediction'] = '続落注意'
        results['risk_level'] = '中'
        results['comment'] = "下落バイアスが強いですが、本格的な加速にはまだ至っていません。"
    else:
        results['final_prediction'] = '底堅い/反発'
        results['risk_level'] = '低'
        results['comment'] = "買い圧力が優勢、またはレンジ下限での反発が見られます。"

    return results
