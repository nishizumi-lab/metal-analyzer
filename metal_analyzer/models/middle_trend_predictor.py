"""中期トレンド分析（日足・週足）ロジックを提供するモジュール。

このモジュールは、以下の概念に基づいて市場の中期的な状態を分析します：
1. 「根雪 (Deep Snow)」: 週足レベルの長期的な上昇トレンド。
2. 「表層雪崩 (Surface Avalanche)」: 短期的な調整や価格の急落。
3. 「高ボラティリティ (Warsh Mode)」: テクニカル指標に基づいたボラティリティの拡大局面。
4. 「深い押し目 (Deep Dip)」: 長期上昇トレンド中の戦略的な買い場。
"""

import pandas as pd
import numpy as np
from ..indicators.sma import calculate_ema, calculate_sma
from ..indicators.rsi import calculate_rsi
from ..indicators.bollinger_bands import calculate_bollinger_bands

def analyze_middle_trend(weekly_df, daily_df):
    """中期的なトレンド分析（YouTube動画で解説されたロジックに基づく）を実行する。

    Args:
        weekly_df (pd.DataFrame): 週足データ。
        daily_df (pd.DataFrame): 日足データ。

    Returns:
        dict: 分析結果を含む辞書。
            - dashboard_1_weekly: 週足トレンド構造（根雪判定）
            - dashboard_2_daily: 日足モメンタム（表層雪崩警戒）
            - dashboard_3_volatility: ボラティリティ体制（高ボラティリティ判定）
            - dashboard_4_strategy: 戦略的エントリー（押し目買い判定）
            - final_prediction: 総合コメント
    """
    results = {
        'dashboard_1_weekly': '不明',
        'dashboard_2_daily': '不明',
        'dashboard_3_volatility': '不明',
        'dashboard_4_strategy': '様子見',
        'final_prediction': ''
    }

    if weekly_df.empty or daily_df.empty:
        results['final_prediction'] = "十分なデータがありません。"
        return results

    # yfinanceがMultiIndexを返す場合の対応
    if isinstance(weekly_df.columns, pd.MultiIndex):
        weekly_df = weekly_df.copy()
        weekly_df.columns = weekly_df.columns.get_level_values(0)
    
    if isinstance(daily_df.columns, pd.MultiIndex):
        daily_df = daily_df.copy()
        daily_df.columns = daily_df.columns.get_level_values(0)

    # =========================================================================
    # --- Dashboard 1: 週足構造 (Deep Snow / 根雪) ---
    # 役割: 長期的な上昇トレンドが崩れていないかを確認する。
    # ロジック: 週足EMA (13, 26, 52) の並び順。
    # =========================================================================
    w_ema13 = calculate_ema(weekly_df, 13).iloc[-1]
    w_ema26 = calculate_ema(weekly_df, 26).iloc[-1]
    w_ema52 = calculate_ema(weekly_df, 52).iloc[-1]
    w_close = weekly_df['Close'].iloc[-1]

    is_weekly_uptrend = False
    
    # パーフェクトオーダー (Close > 13 > 26 > 52) または
    # 価格が短期EMAを割っていても、長期EMA(52)が上昇中で、順序が 13 > 26 > 52 の場合
    if (w_ema13 > w_ema26 > w_ema52):
        if w_close > w_ema13:
            results['dashboard_1_weekly'] = '強気トレンド (Deep Snow 安定)'
            is_weekly_uptrend = True
        elif w_close > w_ema52:
            results['dashboard_1_weekly'] = '調整局面だがトレンド維持 (Deep Snow 継続)'
            is_weekly_uptrend = True # 押し目買いの候補になり得る
        else:
            results['dashboard_1_weekly'] = 'トレンド崩壊の危機 (雪解け警戒)'
    else:
        results['dashboard_1_weekly'] = 'レンジ/下降トレンド'

    # =========================================================================
    # --- Dashboard 2: 日足モメンタム (Surface Alert / 表層雪崩) ---
    # 役割: 直近の下落の強さを測る。
    # ロジック: 日足RSIとMACD (EMA12 - EMA26)。
    # =========================================================================
    d_rsi = calculate_rsi(daily_df, 14).iloc[-1]
    
    d_ema12 = calculate_ema(daily_df, 12)
    d_ema26 = calculate_ema(daily_df, 26)
    d_macd = d_ema12 - d_ema26
    current_macd = d_macd.iloc[-1]
    prev_macd = d_macd.iloc[-2]
    
    is_daily_oversold = d_rsi < 35
    is_momentum_down = current_macd < prev_macd
    
    if is_momentum_down:
        if is_daily_oversold:
            results['dashboard_2_daily'] = '下落過熱 (売られすぎ水準)'
        else:
            results['dashboard_2_daily'] = '下落圧力強 (表層雪崩発生中)'
    else:
        # MACDが上向き
        if current_macd > 0:
            results['dashboard_2_daily'] = '上昇モメンタム (安定)'
        else:
            results['dashboard_2_daily'] = '回復の兆し (雪崩停止)'

    # =========================================================================
    # --- Dashboard 3: ボラティリティ体制 (The Storm / 暴風域) ---
    # 役割: 「ウォーシュ・モード」のような高ボラティリティ環境かどうかを判定。
    # ロジック: 日足ボリンジャーバンド幅の拡大率。
    # =========================================================================
    mb, ub, lb = calculate_bollinger_bands(daily_df, window=20, num_std=2)
    if mb is not None:
        bandwidth = (ub - lb) / mb
        # 過去20日間の平均バンド幅と比較
        avg_bandwidth = bandwidth.rolling(window=20).mean().iloc[-1]
        current_bandwidth = bandwidth.iloc[-1]
        
        # 現在のバンド幅が平均の1.3倍以上なら高ボラティリティ
        if current_bandwidth > avg_bandwidth * 1.3:
            results['dashboard_3_volatility'] = '⚠️ 高ボラティリティ (Warsh Mode)'
        elif current_bandwidth < avg_bandwidth * 0.8:
            results['dashboard_3_volatility'] = '収縮 (Squeeze)'
        else:
            results['dashboard_3_volatility'] = '通常 (Normal)'
    else:
        results['dashboard_3_volatility'] = '計算不可'

    # =========================================================================
    # --- Dashboard 4: 戦略的エントリー (Deep Dip / 深い押し目) ---
    # 役割: 「根雪」が残っている状態で「表層雪崩」が起きた時を狙う。
    # =========================================================================
    
    strategy = "様子見"
    prediction_comment = ""

    if is_weekly_uptrend:
        # 長期トレンドが上向きの場合
        
        if '下落' in results['dashboard_2_daily'] or '過熱' in results['dashboard_2_daily']:
            # 日足が下落中
            if is_daily_oversold or ('回復' in results['dashboard_2_daily']):
                 # 売られすぎ、または回復の兆しがあれば買い
                 strategy = "★ 戦略的買い (Deep Dip Buy)"
                 prediction_comment = "長期トレンドは維持されています。短期的な急落は「表層雪崩」であり、絶好の買い場となる可能性があります（根雪は溶けていません）。"
            else:
                 strategy = "押し目待ち (Wait for Bottom)"
                 prediction_comment = "長期は上ですが、短期的な下げ止まりを待つべきです。落ちてくるナイフに注意。"
        elif '高ボラティリティ' in results['dashboard_3_volatility']:
             strategy = "慎重なトレンドフォロー"
             prediction_comment = "トレンドは上ですが、ボラティリティが高まっています（Warsh Mode）。ポジションサイズを落としてついていく局面です。"
        else:
             strategy = "継続保有 (Hold)"
             prediction_comment = "長期・短期ともに安定しています。利益を伸ばすフェーズです。"
    else:
        # 長期トレンドが崩れている/レンジ
        if is_daily_oversold:
            strategy = "リバウンド狙い (短期)"
            prediction_comment = "全体的なトレンドは弱いため、短期的な自律反発狙いに留めるべきです。"
        else:
            strategy = "売り/静観"
            prediction_comment = "長期トレンドが弱く、積極的な買い場ではありません。"

    results['dashboard_4_strategy'] = strategy
    results['final_prediction'] = prediction_comment

    return results
