"""最新の市場分析結果とチャート画像をDiscordに送信するスクリプト。

短期・中期・長期のトレンド分析を実行し、
結果のEmbedと最新のチャート画像（6枚）をDiscord Webhookに送信します。

Usage:
    python examples/send_gold_trend.py [--dry-run] [--webhook_url URL]
"""

import os
import sys
import argparse
import json
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime
import glob

# プロジェクトルートをパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metal_analyzer import MetalAnalyzer
from metal_analyzer.models.middle_trend_predictor import analyze_middle_trend
from metal_analyzer.models.long_trend_predictor import analyze_long_trend
from metal_analyzer.models.short_trend_predictor import analyze_timeframe_details

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
    
    print("  Gold (Tick Data)...")
    # 短期分析 & チャート生成用
    data['gold_daily'] = yf.download(tickers['Gold'], period="2y", interval="1d", progress=False)
    data['gold_hourly'] = yf.download(tickers['Gold'], period="2mo", interval="1h", progress=False)
    data['gold_15m'] = yf.download(tickers['Gold'], period="1mo", interval="15m", progress=False)
    
    print("  Gold (Long Term)...")
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

def generate_charts(analyzer, output_dir):
    """チャート画像を生成して保存する"""
    print("チャート生成中...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成する時間足とファイル名
    charts = [
        ("Monthly", "chart_01_monthly.png"),
        ("Weekly", "chart_02_weekly.png"),
        ("Daily", "chart_03_daily.png"),
        ("4h", "chart_04_4h.png"),
        ("1h", "chart_05_1h.png"),
        ("15m", "chart_06_15m.png"),
    ]
    
    generated_files = []
    for tf, fname in charts:
        fpath = os.path.join(output_dir, fname)
        # titleはデフォルトに任せるか指定するか
        analyzer.plot_candlestick(tf, filename=fpath, title=f"Gold {tf}")
        if os.path.exists(fpath):
            generated_files.append(fpath)
            
    return generated_files

def run_analyses(data, analyzer):
    """3つのトレンド分析を実行する"""
    results = {}
    
    # 1. 短期トレンド
    print("短期トレンド分析実行中...")
    # analyzerには既にデータがセットされている前提
    results['short'] = analyzer.analyze_short_trend()
    
    # 4時間足データは analyze_short_trend 内で生成されるため、ここで取得可能
    tf_data = {
        'Monthly': data['gold_monthly'],
        'Weekly': data['gold_weekly'],
        'Daily': data['gold_daily'],
        '4H': analyzer.timeframe_data.get('4h'),
        '1H': data['gold_hourly'],
        '15M': data['gold_15m']
    }
    results['short_details'] = analyze_timeframe_details(tf_data)
    
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
    if '極めて高い' in risk_level or 'Crash' in risk_level:
        return 0xFF0000 
    elif '高い' in risk_level or 'Surge' in risk_level:
        return 0xFF4500 
    elif '中' in risk_level:
        return 0xFFFF00 
    else:
        return 0x00FF00 

def create_discord_payload(results):
    """分析結果をDiscord Embed形式に変換する"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    short = results['short']
    middle = results['middle']
    long = results['long']
    
    color = format_color(short.get('risk_level', '低'))
    
    embed = {
        "title": f"📊 Gold Market Trend Report ({now})",
        "description": "Metal Analyzerによる最新の市場分析結果とチャートです。",
        "color": color,
        "fields": [],
        "footer": {
            "text": "Powered by Metal Analyzer"
        }
    }
    
    # --- Short Trend ---
    short_val = f"**予測**: `{short['final_prediction']}`\n"
    short_val += f"**リスク**: {short['risk_level']}\n"
    short_val += f"**センチメント**: {short['dashboard_4_sentiment']}\n"
    short_val += f"> {short['comment']}\n\n"
    short_val += f"👇 **時間足別詳細**\n{results['short_details']}"
    
    embed['fields'].append({
        "name": "🟢 短期トレンド (Short)",
        "value": short_val,
        "inline": False
    })
    
    # --- Middle Trend ---
    mid_val = f"**構造**: {middle['dashboard_1_weekly']}\n"
    mid_val += f"**ボラティリティ**: {middle['dashboard_3_volatility']}\n"
    mid_val += f"**戦略**: `{middle['dashboard_4_strategy']}`\n"
    mid_val += f"> {middle['final_prediction']}"
    
    embed['fields'].append({
        "name": "🟡 中期トレンド (Middle)",
        "value": mid_val,
        "inline": False
    })
    
    # --- Long Trend ---
    long_val = f"**マクロ**: {long['dashboard_3_macro']}\n"
    long_val += f"**相対価値**: {long['dashboard_2_ratio']}\n"
    long_val += f"**推奨PF**: `{long['dashboard_4_portfolio']}`\n"
    long_val += f"> {long['final_prediction']}"

    embed['fields'].append({
        "name": "🟣 長期トレンド (Long)",
        "value": long_val,
        "inline": False
    })
    
    # 添付画像についての注釈なし（自動で表示されるため）
    
    return {"embeds": [embed]}

def send_webhook(url, payload, image_files):
    """Discord Webhookにマルチパートで送信する"""
    # images: list of file paths
    
    files = {}
    # Discordは最大10ファイルまで添付可能
    # file0, file1, ... というキーで送るのが一般的ではないが、
    # request payloadのembedsで url: "attachment://filename" を指定しない場合は
    # 単に添付ファイルとして表示される
    
    open_files = []
    try:
        for i, fpath in enumerate(image_files):
            fname = os.path.basename(fpath)
            f = open(fpath, 'rb')
            open_files.append(f)
            files[f'file{i}'] = (fname, f, 'image/png')
        
        # payload_json フィールドに JSON 文字列を入れる
        data = {'payload_json': json.dumps(payload)}
        
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        print("✅ Discordへの送信に成功しました。")
        
    except Exception as e:
        print(f"❌ 送信エラー: {e}")
        # 詳細なエラー情報を出す
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Server Response: {response.text}")
    finally:
        for f in open_files:
            f.close()

def main():
    parser = argparse.ArgumentParser(description='Send Gold Trend Report with Charts to Discord')
    parser.add_argument('--dry-run', action='store_true', help='Webhookを送信せずにペイロードと生成ファイルを表示します')
    parser.add_argument('--webhook_url', type=str, default=os.getenv('DISCORD_WEBHOOK_URL'), help='Discord Webhook URL')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.webhook_url:
        print("エラー: Webhook URLが指定されていません。")
        return

    # 1. データ取得
    data = get_market_data()
    if data['gold_daily'].empty:
        print("データ取得失敗")
        return

    # 2. Analyzerセットアップ
    analyzer = MetalAnalyzer(ticker="GC=F")
    analyzer.add_timeframe_data("Daily", data['gold_daily'])
    analyzer.add_timeframe_data("1h", data['gold_hourly'])
    analyzer.add_timeframe_data("Monthly", data['gold_monthly'])
    analyzer.add_timeframe_data("Weekly", data['gold_weekly'])
    analyzer.add_timeframe_data("15m", data['gold_15m'])
    
    # 3. 分析実行 (Short分析内で4h足も生成される)
    results = run_analyses(data, analyzer)
    
    # 4. チャート生成
    output_dir = os.path.join("examples", "outputs", "discord")
    image_files = generate_charts(analyzer, output_dir)
    print(f"生成されたチャート: {len(image_files)}枚")

    # 5. Payload作成
    payload = create_discord_payload(results)
    
    # 6. 送信
    if args.dry_run:
        print("\n--- Dry Run: Generated Payload ---")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("--- Generated Files ---")
        for f in image_files:
            print(f)
        print("----------------------------------")
    else:
        print(f"送信先: {args.webhook_url[:30]}...")
        send_webhook(args.webhook_url, payload, image_files)

if __name__ == "__main__":
    main()
