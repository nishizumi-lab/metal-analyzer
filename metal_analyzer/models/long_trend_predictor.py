"""長期トレンド分析（月足レベル）およびマクロ経済分析ロジックを提供するモジュール。

このモジュールは、池水雄一氏の視点に基づき、以下の長期的・マクロ的な視点から分析を行います：
1. 「通貨価値の希薄化 (Debasement)」: ドル建てゴールドの長期トレンドとドルインデックスの動向。
2. 「相対価値 (Relative Value)」: 金銀レシオ (GSR) や金プラチナレシオを用いた割安資産の特定。
3. 「マクロ環境 (Real Rates)」: 実質金利の近似としてのTIPS債券価格動向。
4. 「ポートフォリオ (Portfolio)」: 上記に基づいた貴金属の推奨保有比率。
"""

import pandas as pd
import numpy as np
from ..indicators.sma import calculate_ema

def _ensure_flat_columns(df):
    """MultiIndexのカラムを持つDataFrameをフラットにするヘルパー関数"""
    if df is None or df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    return df

def analyze_long_trend(monthly_gold_df, monthly_silver_df, monthly_platinum_df, monthly_dxy_df, monthly_tips_df):
    """長期的なトレンド分析（池水雄一氏のメソッドに基づく）を実行する。

    Args:
        monthly_gold_df (pd.DataFrame): 金の月足データ。
        monthly_silver_df (pd.DataFrame): 銀の月足データ。
        monthly_platinum_df (pd.DataFrame): プラチナの月足データ。
        monthly_dxy_df (pd.DataFrame): ドルインデックス (DXY) の月足データ。
        monthly_tips_df (pd.DataFrame): TIPS ETF (TIP) の月足データ。

    Returns:
        dict: 分析結果を含む辞書。
    """
    results = {
        'dashboard_1_currency': '不明',
        'dashboard_2_ratio': '不明',
        'dashboard_3_macro': '不明',
        'dashboard_4_portfolio': '不明',
        'final_prediction': ''
    }

    # データの前処理 (MultiIndex対応)
    g_df = _ensure_flat_columns(monthly_gold_df)
    s_df = _ensure_flat_columns(monthly_silver_df)
    p_df = _ensure_flat_columns(monthly_platinum_df)
    dxy_df = _ensure_flat_columns(monthly_dxy_df)
    tips_df = _ensure_flat_columns(monthly_tips_df)

    if g_df is None or g_df.empty:
        results['final_prediction'] = "金のデータが不足しています。"
        return results

    # =========================================================================
    # --- Dashboard 1: 通貨価値とゴールド (Currency Devaluation) ---
    # 役割: 「無国籍通貨」としての金の価値上昇と、法定通貨（ドル）の減価を確認。
    # ロジック: 金の長期EMA(12, 24ヶ月)と、ドルインデックスのトレンド比較。
    # =========================================================================
    g_close = g_df['Close'].iloc[-1]
    g_ema12 = calculate_ema(g_df, 12).iloc[-1]
    g_ema24 = calculate_ema(g_df, 24).iloc[-1]
    
    gold_trend = "中立"
    if g_close > g_ema12 > g_ema24:
        gold_trend = "長期上昇 (通貨価値下落)"
    elif g_close < g_ema12 < g_ema24:
        gold_trend = "長期調整"

    dxy_trend = "不明"
    if dxy_df is not None and not dxy_df.empty:
        dxy_close = dxy_df['Close'].iloc[-1]
        dxy_ema12 = calculate_ema(dxy_df, 12).iloc[-1]
        if dxy_close < dxy_ema12:
            dxy_trend = "ドル安トレンド (金に追い風)"
        else:
            dxy_trend = "ドル高傾向 (金に逆風)"
    
    results['dashboard_1_currency'] = f"{gold_trend} / {dxy_trend}"

    # =========================================================================
    # --- Dashboard 2: 相対価値分析 (Ratio Analysis) ---
    # 役割: 金に対して割安な貴金属（銀・プラチナ）を探す。池水氏は銀やプラチナのキャッチアップに注目。
    # ロジック: 直近のGSR, Gold/Platinum Ratioを計算。
    # =========================================================================
    ratio_comment = []
    
    # 金銀レシオ (GSR)
    if s_df is not None and not s_df.empty:
        s_close = s_df['Close'].iloc[-1]
        gsr = g_close / s_close
        if gsr > 80:
            ratio_comment.append(f"銀が歴史的割安 (GSR: {gsr:.1f})")
        elif gsr < 60:
            ratio_comment.append(f"銀の割安感解消 (GSR: {gsr:.1f})")
        else:
            ratio_comment.append(f"GSR適正圏 (GSR: {gsr:.1f})")
    
    # 金プラチナレシオ
    if p_df is not None and not p_df.empty:
        p_close = p_df['Close'].iloc[-1]
        gpr = g_close / p_close
        if gpr > 2.0:
             ratio_comment.append(f"プラチナ超割安 (倍率: {gpr:.1f})")
        elif gpr > 1.0:
             ratio_comment.append(f"プラチナ割安 (倍率: {gpr:.1f})")
        else:
             ratio_comment.append(f"プラチナ高値 (倍率: {gpr:.1f})")

    results['dashboard_2_ratio'] = ", ".join(ratio_comment) if ratio_comment else "データ不足"

    # =========================================================================
    # --- Dashboard 3: マクロ環境 (Macro Environment / Real Rates) ---
    # 役割: 実質金利の動向。実質金利が低い（マイナス）ほど金は輝く。
    # ロジック: TIPS ETF (TIP) が上昇していれば実質金利低下（金利低下期待 or インフレ期待）。
    # =========================================================================
    macro_view = "中立"
    if tips_df is not None and not tips_df.empty:
        tips_close = tips_df['Close'].iloc[-1]
        tips_ema12 = calculate_ema(tips_df, 12).iloc[-1]
        
        if tips_close > tips_ema12:
            macro_view = "実質金利低下傾向 (金に強力な追い風)"
        else:
            macro_view = "実質金利上昇傾向 (金の上値重い)"
            
    results['dashboard_3_macro'] = macro_view

    # =========================================================================
    # --- Dashboard 4: ポートフォリオ判定 (Portfolio Logic) ---
    # 役割: すべてを勘案して推奨保有比率を提示。池水氏は通常10-20%、強気ならそれ以上を推奨。
    # =========================================================================
    score = 0
    if "上昇" in gold_trend: score += 2
    if "ドル安" in dxy_trend: score += 1
    if "割安" in results['dashboard_2_ratio']: score += 1 # 銀やプラチナの魅力
    if "低下" in macro_view: score += 2 # 実質金利低下は最強のファンダメンタルズ

    allocation = "5-10% (標準・保守的)"
    comment = ""

    if score >= 5:
        allocation = "20-25% (積極投資)"
        comment = "全指標が好転しています。法定通貨のリスクヘッジとして、そして値上がり益を狙う資産として最大級の組み入れを推奨します。銀やプラチナへの分散も効果的です。"
    elif score >= 3:
        allocation = "10-15% (買い増し推奨)"
        comment = "ファンダメンタルズは良好です。押し目を見つけてポートフォリオの比率を高めるべき局面です。"
    else:
        allocation = "5% (最低限のヘッジ)"
        comment = "マクロ環境は逆風ですが、保険としての保有は継続すべきです。積極的な買い増しはマクロ指標の好転を待ちましょう。"

    results['dashboard_4_portfolio'] = allocation
    results['final_prediction'] = comment

    return results
