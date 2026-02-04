# 実装計画 - 長期トレンド予測 (Long Trend Predictor)

## ゴール (Goal Description)
池水雄一氏の分析手法に基づき、長期的な視点（数年単位）での貴金属トレンドを分析する `metal_analyzer/models/long_trend_predictor.py` を実装します。
チャートの形状だけでなく、マクロ経済指標（金利、インフレ率）や貴金属間の相対価格（レシオ）を用いて、金・銀・プラチナの本質的な価値と割安度を判定します。

## ユーザーレビュー必須事項 (User Review Required)
> [!IMPORTANT]
> 外部の「実質金利（米国債利回り - インフレ率）」データはリアルタイム取得が難しいため、`yfinance` で取得可能な代替指標（**TIPS ETF (TIP)** や **ドルインデックス (DX-Y.NYB)**）を使用し、近似的にマクロ環境を推定します。

## 変更案 (Proposed Changes)

### `metal_analyzer/models`

#### [NEW] [long_trend_predictor.py](file:///c:/github/metal-analyzer/metal_analyzer/models/long_trend_predictor.py)
- **関数**: `analyze_long_trend(monthly_df, silver_monthly_df, platinum_monthly_df, macro_data)`
- **ロジック概要**:
    - **ダッシュボード 1: 通貨価値とゴールド (Currency Devaluation)**
        - **ドル建てゴールドの長期推移**: 月足EMAの長期トレンド判定。
        - **対通貨パフォーマンス**: ドルインデックス (DXY) との逆相関を確認。「ドル安・金高」のトレンドが継続しているか。
    - **ダッシュボード 2: 相対価値分析 (Ratio Analysis)**
        - **金銀レシオ (Gold/Silver Ratio)**: (金価格 / 銀価格)。歴史的高水準なら銀の割安判断。
        - **金プラチナレシオ**: (金価格 / プラチナ価格)。プラチナの割安判断。
    - **ダッシュボード 3: マクロ環境 (Macro Environment)**
        - **実質金利の近似**: TIPS (米国物価連動国債) のトレンドを使用。TIPS上昇（実質金利低下）なら金に追い風。
    - **ダッシュボード 4: ポートフォリオ判定 (Portfolio Logic)**
        - 上記すべてを勘案し、ポートフォリオへの組み入れ推奨度（アグレッシブ 25% / 標準 10% / 保守的 5%）を提示。

## 検証計画 (Verification Plan)

### 自動テスト (Automated Tests)
- `examples/verify_long_trend.py` を作成。
- 金、銀、プラチナ、ドルインデックス、TIPSの過去データを取得し、長期的（10年以上）なトレンド判定とポートフォリオ推奨が出力されるか確認します。
