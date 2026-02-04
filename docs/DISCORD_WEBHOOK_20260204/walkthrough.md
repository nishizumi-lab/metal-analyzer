# Discord通知プログラム実装完了

最新の市場データに基づいた短期・中期・長期のトレンド分析結果を、Discordに自動送信するスクリプトを作成しました。

## 実装内容

### プログラム: `examples/send_gold_trend.py`

このスクリプトは以下のフローで動作します。

1. **データ取得**: `yfinance` で金、銀、プラチナ、DXY、TIPSのデータを一括取得
2. **分析実行**:
    - **Short Trend**: 4つのダッシュボード分析
    - **Middle Trend**: 根雪・表層雪崩・Warsh Mode分析
    - **Long Trend**: マクロ・ポートフォリオ分析
3. **通知**: 分析結果を整形し、Discord WebhookにEmbed形式で送信

### 使い方

```bash
# テスト実行（送信せずに内容を表示）
python examples/send_gold_trend.py --dry-run

# 実際の送信
# 方法1: 引数で指定
python examples/send_gold_trend.py --webhook_url https://discord.com/api/webhooks/...

# 方法2: 環境変数を使用 (推奨)
# Windows (PowerShell)
$env:DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
python examples/send_gold_trend.py
```

## 通知イメージ (Dry Run結果)

```json
{
  "title": "📊 Gold Market Trend Report (2026-02-04 15:00)",
  "color": 65280,
  "fields": [
    {
      "name": "🟢 短期トレンド (Short Trend)",
      "value": "**予測**: `底堅い/反発`\n**リスク**: 低\n..."
    },
    {
      "name": "🟡 中期トレンド (Middle Trend)",
      "value": "**構造**: 強気トレンド (Deep Snow 安定)\n**戦略**: `慎重なトレンドフォロー`\n..."
    },
    {
      "name": "🟣 長期トレンド (Long Trend)",
      "value": "**推奨PF**: `20-25% (積極投資)`\n..."
    }
  ]
}
```
