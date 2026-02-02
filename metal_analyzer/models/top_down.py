from ..indicators.sma import calculate_sma
from ..indicators.rsi import calculate_rsi

def analyze_top_down(daily_data, hourly_data):
    """トップダウン分析を実行し、日足と1時間足を組み合わせて判定を行う。

    Args:
        daily_data (pd.DataFrame): 日足のデータフレーム。
        hourly_data (pd.DataFrame): 1時間足のデータフレーム。

    Returns:
        tuple: (signal, prediction, daily_trend, hourly_trend, hourly_rsi) のタプル。
    """
    if daily_data.empty or hourly_data.empty:
        return "様子見 (Wait)", "データがありません。", "不明", "不明", 0

    # Step 1: 日足分析 (長期トレンド)
    daily_sma20 = calculate_sma(daily_data, 20).iloc[-1]
    daily_sma50 = calculate_sma(daily_data, 50).iloc[-1]
    current_daily_close = daily_data['Close'].iloc[-1]
    
    daily_trend = "レンジ/不明"
    if current_daily_close > daily_sma20 > daily_sma50:
        daily_trend = "上昇 (Uptrend)"
    elif current_daily_close < daily_sma20 < daily_sma50:
        daily_trend = "下降 (Downtrend)"

    # Step 2: 1時間足分析 (短期状況)
    hourly_rsi = calculate_rsi(hourly_data, 14).iloc[-1]
    hourly_sma20 = calculate_sma(hourly_data, 20).iloc[-1]
    current_hourly_close = hourly_data['Close'].iloc[-1]
    
    hourly_trend = "レンジ/不明"
    if current_hourly_close > hourly_sma20:
         hourly_trend = "短期上昇"
    elif current_hourly_close < hourly_sma20:
         hourly_trend = "短期下降"

    # Step 3: 総合判定 (シグナル)
    signal = "様子見 (Wait)"
    prediction = "明確な方向感が出るまで待機推奨。"
    
    if "上昇" in daily_trend and "短期上昇" in hourly_trend:
        if hourly_rsi < 70:
            signal = "買い (STRONG BUY)"
            prediction = "長期・短期共に上昇トレンド。押し目買いの好機。直近高値を目指す展開を予想。"
        else:
            signal = "買い検討 (Wait for Dip)"
            prediction = "トレンドは強いが短期的に過熱感あり。少し調整が入ったところを狙いたい。"
            
    elif "下降" in daily_trend and "短期下降" in hourly_trend:
        if hourly_rsi > 30:
            signal = "売り (STRONG SELL)"
            prediction = "長期・短期共に下降トレンド。戻り売り優勢。直近安値を更新する展開を予想。"
        else:
            signal = "売り検討 (Wait for Pullback)"
            prediction = "下落トレンド継続中だが、短期的に売られすぎ。一時的な反発に注意。"
    
    elif "上昇" in daily_trend and "短期下降" in hourly_trend:
         prediction = "長期的には上昇だが、短期的には調整局面。サポートラインでの反発を確認できれば買い。"
    
    elif "下降" in daily_trend and "短期上昇" in hourly_trend:
         prediction = "長期的には下降だが、短期的には反発局面。レジスタンスラインでの反落を確認できれば売り。"

    return signal, prediction, daily_trend, hourly_trend, hourly_rsi
