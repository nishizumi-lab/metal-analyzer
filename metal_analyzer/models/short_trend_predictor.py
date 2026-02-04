"""短期トレンド分析ロジックを提供するモジュール。

このモジュールは、4つの異なる視点（ダッシュボード）から市場を分析し、
短期的なトレンド予測とリスク評価を行う関数を提供します。
"""

import pandas as pd
import numpy as np
from ..indicators.sma import calculate_ema, calculate_sma
from ..indicators.rsi import calculate_rsi
from ..patterns import detect_double_top, detect_double_bottom

def analyze_short_trend(daily_df, h4_df, h1_df, patterns=None):
    """短期的な4つのダッシュボード指標に基づいたトレンド分析を実行する。

    以下の4つの観点からスコアリングを行います：
    1. 長期トレンド (EMA Perfect Order)
    2. モメンタム (EMA乖離)
    3. ボラティリティ加速
    4. センチメント (重要ライン・パターン)

    Args:
        daily_df (pd.DataFrame): 日足データ。
        h4_df (pd.DataFrame): 4時間足データ。
        h1_df (pd.DataFrame): 1時間足データ。
        patterns (dict, optional): 検知されたチャートパターン情報。
            例: {'double_top': True, 'neckline': 2500.0}

    Returns:
        dict: 分析結果を含む辞書。
            - dashboard_1~4: 各区分の判定結果
            - final_prediction: 最終的な方向性予測
            - risk_level: リスク評価
            - comment: 詳細コメント
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

    # データ不足チェック
    if daily_df.empty or h4_df.empty or h1_df.empty:
        results['comment'] = "十分なデータがありません。"
        return results

    # =========================================================================
    # --- Dashboard 1: 長期トレンド分析 (EMAパーフェクトオーダー) ---
    # 役割: 相場の「大きな流れ」がどちらを向いているかを判定します。
    # ロジック: 20日, 50日, 200日のEMA（指数平滑移動平均）の並び順を確認。
    # =========================================================================
    h4_ema20 = calculate_ema(h4_df, 20).iloc[-1]
    h4_ema50 = calculate_ema(h4_df, 50).iloc[-1]
    h4_ema200 = calculate_ema(h4_df, 200).iloc[-1]
    h4_close = h4_df['Close'].iloc[-1]

    # 下落のパーフェクトオーダー: 短期 < 中期 < 長期 の順で、価格が一番下にある状態
    if h4_close < h4_ema20 < h4_ema50 < h4_ema200:
        results['dashboard_1_trend'] = 'パーフェクトオーダー (強気下降)'
    # 上昇のパーフェクトオーダー: 長期 < 中期 < 短期 の順で、価格が一番上にある状態
    elif h4_close > h4_ema20 > h4_ema50 > h4_ema200:
        results['dashboard_1_trend'] = 'パーフェクトオーダー (強気上昇)'
    else:
        results['dashboard_1_trend'] = 'トレンド転換点/混在'

    # =========================================================================
    # --- Dashboard 2: モメンタム分析 (EMA乖離率) ---
    # 役割: 現在の価格が「行き過ぎ」ていないか、あるいは強い勢いがあるかを判定します。
    # ロジック: 1時間足の現在値とEMA 20 deltas を計算。
    # =========================================================================
    h1_ema20 = calculate_ema(h1_df, 20).iloc[-1]
    h1_close = h1_df['Close'].iloc[-1]
    dist_ema20 = (h1_close - h1_ema20) / h1_ema20
    
    # 0.5% 以上の乖離を一つの基準として勢いを判定
    if dist_ema20 < -0.005:
        results['dashboard_2_momentum'] = '下落の勢い強い'
    elif dist_ema20 > 0.005:
        results['dashboard_2_momentum'] = '上昇の勢い強い'
    else:
        results['dashboard_2_momentum'] = '穏やか'

    # =========================================================================
    # --- Dashboard 3: ボラティリティ分析 (価格変動の加速) ---
    # 役割: 相場が「動き始めた」タイミング（爆発力）を検知します。
    # ロジック: 直近3本のローソク足の平均値幅を、過去20本の平均値幅と比較。
    # =========================================================================
    recent_range = (h1_df['High'] - h1_df['Low']).tail(3).mean()
    avg_range = (h1_df['High'] - h1_df['Low']).tail(20).mean()
    
    # 値幅が平均の1.5倍を超えたら「加速状態」とみなす
    if recent_range > avg_range * 1.5:
        results['dashboard_3_volatility'] = 'ブレイクアウト/加速中'
        accel_factor = 1.5 # 予測スコアに倍率をかける
    else:
        results['dashboard_3_volatility'] = '安定'
        accel_factor = 1.0

    # =========================================================================
    # --- Dashboard 4: 市場センチメント (重要ライン・パターン) ---
    # 役割: 決定的な節目（サポート・レジスタンス）の突破やパターンを判定。
    # ロジック: 直近50本の高値・安値の更新、およびダブルトップ等のパターン検知。
    #          さらに、反発（リバーサル）の予兆として「200EMAサポート」「RSIダイバージェンス」「ピンバー」「ダブルボトム」も監視。
    # =========================================================================
    h1_low_50 = h1_df['Low'].tail(50).min()
    h1_high_50 = h1_df['High'].tail(50).max()
    
    # 追加指標の計算 (RSI, 200EMA, Pinbar)
    rsi_series = calculate_rsi(h1_df, 14)
    h1_rsi = rsi_series.iloc[-1]
    
    h1_ema200 = calculate_ema(h1_df, 200).iloc[-1]
    
    # ピンバー判定 (下ヒゲが実体の2倍以上)
    last_candle = h1_df.iloc[-1]
    body_size = abs(last_candle['Close'] - last_candle['Open'])
    lower_shadow = min(last_candle['Close'], last_candle['Open']) - last_candle['Low']
    is_pinbar = (lower_shadow > body_size * 2.0) and (lower_shadow > 0)

    # 200EMAサポート判定 (価格が200EMA付近にあるか)
    # 現在価格が200EMAの上下0.2%以内にあり、かつRSIが極端な売られすぎでない
    dist_ema200 = (h1_close - h1_ema200) / h1_ema200
    is_200ema_support = (abs(dist_ema200) < 0.002)
    
    # RSIダイバージェンス (簡易版: 価格は安値更新、RSIは切り上がり)
    # 直近15本の最安値時点のRSIと、現在のRSIを比較
    recent_low_idx = h1_df['Low'].tail(15).idxmin()
    recent_low_rsi = rsi_series.loc[recent_low_idx]
    # 現在価格が直近安値以下、かつ現在のRSIが当時のRSIより高い (+3ポイント以上)
    is_bullish_divergence = (h1_close <= h1_df.loc[recent_low_idx, 'Low']) and (h1_rsi > recent_low_rsi + 3.0)

    pattern_risk = 0
    sentiment_desc = 'レンジ内'

    # チャートパターンによる判定 (優先度: 高)
    detected_top = patterns.get('double_top') if patterns else False
    detected_bottom = patterns.get('double_bottom') if patterns else False

    if detected_top:
        neckline = patterns.get('neckline_top', 0)
        if h1_close < neckline:
            sentiment_desc = '重要ライン割れ (暴落確定)'
            pattern_risk = -5
        else:
            sentiment_desc = '重要ラインでの攻防 (Top)'
    elif detected_bottom:
        neckline = patterns.get('neckline_bottom', 0)
        if h1_close > neckline:
            sentiment_desc = 'Wボトム ネックライン上抜け (反発確定)'
            pattern_risk = 5
        else:
             sentiment_desc = 'Wボトム形成中 (反発期待)'
             pattern_risk = 2
    else:
        # 特別なパターンがない場合は、各種反発シグナルなどを評価
        
        # 強力な買いシグナル (V字回復/押し目買い)
        if is_pinbar and (h1_rsi < 45 or is_200ema_support):
            sentiment_desc = '強力な反発シグナル (Pinbar + Support)'
            pattern_risk = 4 # 強い買い
        elif is_bullish_divergence:
            sentiment_desc = 'RSIダイバージェンス (底打ち示唆)'
            pattern_risk = 3
        elif is_200ema_support:
            sentiment_desc = '200EMAサポート (押し目)'
            pattern_risk = 2
        elif h1_close <= h1_low_50:
            sentiment_desc = '新安値更新'
            pattern_risk = -2
        elif h1_close >= h1_high_50:
            sentiment_desc = '新高値更新'
            pattern_risk = 2
        else:
             sentiment_desc = 'レンジ内'
            
    results['dashboard_4_sentiment'] = sentiment_desc

    # =========================================================================
    # --- 最終分析アルゴリズム (スコアリングシステム) ---
    # 役割: 4つのダッシュボードの結果を統合し、最終分析結果を導き出します。
    # =========================================================================
    score = 0
    # 1. 長期トレンドの影響 (配点: +/- 3)
    if '下降' in results['dashboard_1_trend']: score -= 3
    if '上昇' in results['dashboard_1_trend']: score += 3
    
    # 2. モメンタムの影響 (配点: +/- 1)
    if '下落' in results['dashboard_2_momentum']: score -= 1
    if '上昇' in results['dashboard_2_momentum']: score += 1
    
    # 3. センチメントと、ボラティリティによる増幅
    # (score + 重要ライン割れリスク) に対して、値幅が拡大していれば最大1.5倍の加重を行う
    score = (score + pattern_risk) * accel_factor

    # スコアに基づいた最終判定の分類
    if score <= -6:
        results['final_prediction'] = '⚠️ 大暴落加速 (Great Crash Acceleration)'
        results['risk_level'] = '極めて高い'
        results['comment'] = "長期下降トレンド、重要ライン割れ、ボラティリティ拡大が全て揃いました。トレンドの底が見えません。"
    elif score >= 5: # 基準を緩和 (6 -> 5) し、反発を捉えやすくする
        results['final_prediction'] = '🚀 急騰加速 (Surge Acceleration)'
        results['risk_level'] = '高い'
        results['comment'] = "レジスタンス突破、または強力なサポートからの急反発（V字回復）が発生しています。"
    elif score < 0:
        results['final_prediction'] = '続落注意'
        results['risk_level'] = '中'
        results['comment'] = "下落バイアスが強いですが、反発の予兆がないかセンチメント（ピンバー等）を注視してください。"
    else:
        results['final_prediction'] = '底堅い/反発'
        results['risk_level'] = '低'
        results['comment'] = "買い圧力が優勢です。押し目買いやレンジ下限での反発の好機となる可能性があります。"

    return results

def analyze_timeframe_details(timeframes):
    """各時間足の詳細分析レポートを生成する。

    Args:
        timeframes (dict): 時間足名をキー、DataFrameを値とする辞書。
                           例: {'Monthly': df, 'Weekly': df ...}

    Returns:
        str: 整形された分析レポート文字列。
    """
    details = []
    # 表示順序を固定
    order = ['Monthly', 'Weekly', 'Daily', '4H', '1H', '15M']
    
    for tf_name in order:
        if tf_name not in timeframes:
            continue
            
        df = timeframes[tf_name]
        if df is None or df.empty:
            continue
            
        # --- トレンド判定 (EMA) ---
        # 必要な期間の長さがあるか確認
        if len(df) < 50:
            trend = "データ不足"
        else:
            ema20 = calculate_ema(df, 20).iloc[-1]
            ema50 = calculate_ema(df, 50).iloc[-1]
            ema200 = calculate_ema(df, 200).iloc[-1]
            close = df['Close'].iloc[-1]
            
            if close > ema20 > ema50 > ema200:
                trend = "🔼 上昇 (価格 > EMA20 > 50 > 200)"
            elif close < ema20 < ema50 < ema200:
                trend = "🔽 下落 (価格 < EMA20 < 50 < 200)"
            elif close > ema200:
                trend = "↗️ 上昇 (EMA200上)"
            elif close < ema200:
                trend = "↘️ 下落 (EMA200下)"
            else:
                trend = "→ 混在"

        # --- パターン検知 ---
        pattern_str = ""
        # 1h足以外でも検知できるように、モデルの関数を直接呼ぶ
        if len(df) > 50:
            is_dt, _ = detect_double_top(df)
            is_db, _ = detect_double_bottom(df)
            
            if is_dt: pattern_str += "**⚠️ Wトップ** "
            if is_db: pattern_str += "**💎 Wボトム** "

        # 行の作成
        row = f"**{tf_name}**: `{trend}` {pattern_str}"
        details.append(row)
        
    return "\n".join(details)
