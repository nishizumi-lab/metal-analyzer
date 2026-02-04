# 実装計画 - Discord通知プログラム (send_gold_trend.py)

## ゴール (Goal Description)
最新の市場データを用いて「短期・中期・長期」の全てのトレンド分析を実行し、その結果を整形してDiscordのWebhookに送信するスクリプト `examples/send_gold_trend.py` を作成します。
定期実行（cronなど）を想定し、環境変数からWebhook URLを読み込む仕様とします。

## ユーザーレビュー必須事項 (User Review Required)
> [!IMPORTANT]
> 実行には `DISCORD_WEBHOOK_URL` 環境変数の設定、またはスクリプト実行時の引数指定が必要です。
> `requests` ライブラリを使用するため、未インストールの場合は `pip install requests` が必要になります。

## 変更案 (Proposed Changes)

### `examples/`

#### [NEW] [send_gold_trend.py](file:///c:/github/metal-analyzer/examples/send_gold_trend.py)
- **機能**:
    1. **データ取得**: yfinanceを使用して、短期・中期・長期分析に必要な全データ（金、銀、プラチナ、DXY、TIPS）を一括取得。
    2. **分析実行**:
        - `analyzer.analyze_short_trend()`
        - `analyze_middle_trend(weekly, daily)`
        - `analyze_long_trend(gold, silver, platinum, dxy, tips)`
    3. **Payload作成**: DiscordのEmbed形式に整形。
        - **Title**: Gold Market Trend Report (YYYY-MM-DD)
        - **Fields**:
            - 🟢 **Short Trend**: 予測、リスク、ダッシュボード結果
            - 🟡 **Middle Trend**: 根雪/表層雪崩判定、戦略
            - 🟣 **Long Trend**: ポートフォリオ推奨、マクロ環境
    4. **送信**: `requests.post` でWebhookにPOST送信。

## 検証計画 (Verification Plan)

### 自動テスト (Automated Tests)
- `examples/send_gold_trend.py` に `--dry-run` オプションを実装し、実際に送信せずに生成されたJSON Payloadを標準出力で確認できるようにします。
- ユーザーにWebhook URLを設定してもらい、実際に通知が届くか確認してもらいます。
