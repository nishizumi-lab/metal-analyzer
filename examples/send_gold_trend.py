"""最新の市場分析結果をDiscordに送信するスクリプト。

短期・中期・長期の全てのトレンド分析を実行し、
結果を見やすいEmbed形式で指定されたDiscord Webhookに送信します。

Usage:
    python examples/send_gold_trend.py [--dry-run] [--webhook_url URL]

    環境変数 DISCORD_WEBHOOK_URL が設定されている場合、引数は省略可能です。
"""

import os
import sys
import argparse
import json
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metal_analyzer import MetalAnalyzer
from metal_analyzer.models.middle_trend_predictor import analyze_middle_trend
from metal_analyzer.models.long_trend_predictor import analyze_long_trend

def get_market_data():
    """分析に必要な全データを取得する"""
    print("データ取得中...")
    tickers = {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Platinum": "PL=F",
        "DXY": "DX-Y.NYB",
        "TIPS": "TIP"
    }
    
    data = {}
    
    # 短期・中期・長期で必要なデータ範囲をカバー
    # 日足: 過去2年, 時間足: 過去2ヶ月, 月足: 過去15年
    
    print("  Gold (Short/Middle/Long)...")
    data['gold_daily'] = yf.download(tickers['Gold'], period="2y", interval="1d", progress=False)
    data['gold_hourly'] = yf.download(tickers['Gold'], period="2mo", interval="1h", progress=False)
    data['gold_weekly'] = yf.download(tickers['Gold'], period="5y", interval="1wk", progress=False)
    data['gold_monthly'] = yf.download(tickers['Gold'], period="15y", interval="1mo", progress=False)

    print("  Silver (Long)...")
    data['silver_monthly'] = yf.download(tickers['Silver'], period="15y", interval="1mo", progress=False)
    
    print("  Platinum (Long)...")
    data['platinum_monthly'] = yf.download(tickers['Platinum'], period="15y", interval="1mo", progress=False)
    
    print("  Macro (DXY, TIPS)...")
    data['dxy_monthly'] = yf.download(tickers['DXY'], period="15y", interval="1mo", progress=False)
    data['tips_monthly'] = yf.download(tickers['TIPS'], period="15y", interval="1mo", progress=False)
    
    return data

def run_analyses(data):
    """3つのトレンド分析を実行する"""
    results = {}
    
    # 1. 短期トレンド
    print("短期トレンド分析実行中...")
    analyzer = MetalAnalyzer(ticker="GC=F")
    analyzer.set_multi_timeframe_data(data['gold_daily'], data['gold_hourly'])
    # 4時間足は1時間足から生成される
    results['short'] = analyzer.analyze_short_trend()
    
    # 2. 中期トレンド
    print("中期トレンド分析実行中...")
    results['middle'] = analyze_middle_trend(data['gold_weekly'], data['gold_daily'])
    
    # 3. 長期トレンド
    print("長期トレンド分析実行中...")
    results['long'] = analyze_long_trend(
        data['gold_monthly'],
        data['silver_monthly'],
        data['platinum_monthly'],
        data['dxy_monthly'],
        data['tips_monthly']
    )
    
    return results

def format_color(risk_level):
    """リスクレベルに応じて色（整数）を返す"""
    if '極めて高い' in risk_level or 'Crash' in risk_level:
        return 0xFF0000 # Red
    elif '高い' in risk_level or 'Surge' in risk_level:
        return 0xFF4500 # Orange Red
    elif '中' in risk_level:
        return 0xFFFF00 # Yellow
    else:
        return 0x00FF00 # Green

def create_discord_payload(results):
    """分析結果をDiscord Embed形式に変換する"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    short = results['short']
    middle = results['middle']
    long = results['long']
    
    # メインカラーは短期トレンドのリスクレベルに基づく
    color = format_color(short.get('risk_level', '低'))
    
    embed = {
        "title": f"📊 Gold Market Trend Report ({now})",
        "description": "Metal Analyzerによる最新の市場分析結果です。",
        "color": color,
        "fields": [],
        "footer": {
            "text": "Powered by Metal Analyzer"
        }
    }
    
    # --- Short Trend Field ---
    short_val = f"**予測**: `{short['final_prediction']}`\n"
    short_val += f"**リスク**: {short['risk_level']}\n"
    short_val += f"**センチメント**: {short['dashboard_4_sentiment']}\n"
    short_val += f"> {short['comment']}"
    
    embed['fields'].append({
        "name": "🟢 短期トレンド (Short Trend)",
        "value": short_val,
        "inline": False
    })
    
    # --- Middle Trend Field ---
    mid_val = f"**構造**: {middle['dashboard_1_weekly']}\n"
    mid_val += f"**ボラティリティ**: {middle['dashboard_3_volatility']}\n"
    mid_val += f"**戦略**: `{middle['dashboard_4_strategy']}`\n"
    mid_val += f"> {middle['final_prediction']}"
    
    embed['fields'].append({
        "name": "🟡 中期トレンド (Middle Trend)",
        "value": mid_val,
        "inline": False
    })
    
    # --- Long Trend Field ---
    long_val = f"**マクロ環境**: {long['dashboard_3_macro']}\n"
    long_val += f"**相対価値**: {long['dashboard_2_ratio']}\n"
    long_val += f"**推奨PF**: `{long['dashboard_4_portfolio']}`\n"
    long_val += f"> {long['final_prediction']}"

    embed['fields'].append({
        "name": "🟣 長期トレンド (Long Trend)",
        "value": long_val,
        "inline": False
    })
    
    payload = {
        "username": "Metal Analyzer Bot",
        "embeds": [embed]
    }
    
    return payload

def send_webhook(url, payload):
    """Discord Webhookに送信する"""
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        print("✅ Discordへの送信に成功しました。")
    except Exception as e:
        print(f"❌ 送信エラー: {e}")

def main():
    parser = argparse.ArgumentParser(description='Send Gold Trend Report to Discord')
    parser.add_argument('--dry-run', action='store_true', help='Webhookを送信せずにペイロードを表示します')
    parser.add_argument('--webhook_url', type=str, default=os.getenv('DISCORD_WEBHOOK_URL'), help='Discord Webhook URL')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.webhook_url:
        print("エラー: Webhook URLが指定されていません。環境変数 DISCORD_WEBHOOK_URL を設定するか、--webhook_url 引数を使用してください。")
        print("テストのみ行う場合は --dry-run を指定してください。")
        return

    # 1. データ取得
    data = get_market_data()
    
    if data['gold_daily'].empty:
        print("データ取得に失敗したため終了します。")
        return

    # 2. 分析実行
    results = run_analyses(data)
    
    if results.get('short') is None:
        print("短期分析に失敗しました。")
        return

    # 3. Payload作成
    payload = create_discord_payload(results)
    
    # 4. 送信または表示
    if args.dry_run:
        print("\n--- Dry Run: Generated Payload ---")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("----------------------------------")
    else:
        print(f"送信先: {args.webhook_url[:30]}...")
        send_webhook(args.webhook_url, payload)

if __name__ == "__main__":
    main()
