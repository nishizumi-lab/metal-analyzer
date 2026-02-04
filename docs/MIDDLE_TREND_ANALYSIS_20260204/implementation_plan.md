# 実装計画 - 中期トレンド予測 (Middle Trend Predictor)

## ゴール (Goal Description)
中期的な分析（日足および週足）を提供する `metal_analyzer/models/middle_trend_predictor.py` を実装します。
このモジュールは、指定されたYouTube動画の洞察（「高ボラティリティ」環境の特定、短期的な暴落「表層雪崩」と長期トレンド「根雪」の区別、および戦略的なエントリーポイント「深い押し目」の検知）をシステム化することを目的としています。

## ユーザーレビュー必須事項 (User Review Required)
> [!IMPORTANT]
> システムにはリアルタイムのニュースフィードがないため、「ウォーシュ・モード」や「高ボラティリティ」の判定は、ニュースのセンチメントではなく、テクニカル指標（ATRやボリンジャーバンド幅）を使用して実装します。

## 変更案 (Proposed Changes)

### `metal_analyzer/models`

#### [NEW] [middle_trend_predictor.py](file:///c:/github/metal-analyzer/metal_analyzer/models/middle_trend_predictor.py)
- **関数**: `analyze_middle_trend(weekly_df, daily_df)`
- **ロジック概要**:
    - **ダッシュボード 1: 週足構造 (根雪 / Deep Snow)**
        - 週足のEMA (13, 26, 52など) を使用して、根底にある長期トレンド（プライマリートレンド）を判定します。
    - **ダッシュボード 2: 日足モメンタム (表層の警戒 / Surface Alert)**
        - 日足のMACDやRSIを使用して、直近の調整局面や下落の勢いを検知します。
    - **ダッシュボード 3: ボラティリティ体制 (嵐 / The Storm)**
        - 日足のボリンジャーバンド幅やATR（Average True Range）を使用して、市場が「高ボラティリティ（警戒）」状態か「安定」状態かを分類します。
    - **ダッシュボード 4: 戦略的エントリー (押し目買い / Dip Buying)**
        - 「週足が上昇トレンド」かつ「日足が売られすぎ/サポート到達」の条件を組み合わせ、「戦略的な買い（Dip Buy）」シグナルを出します（動画の「上昇トレンドへの回帰」という論拠に合致させます）。

### `metal_analyzer/indicators`
(変更なし。既存の `sma.py`, `rsi.py`, `bollinger_bands.py` を使用します。MACDが必要な場合は、既存のEMA計算を組み合わせてローカルで計算するか、必要に応じて追加します。)

## 検証計画 (Verification Plan)

### 自動テスト (Automated Tests)
- 専用の検証用スクリプト `examples/verify_middle_trend.py` を作成します。
- **テストケース 1**: 「上昇トレンド中の暴落」を模したデータ（直近のユーザーデータや過去データ）で実行し、「高ボラティリティ」および「押し目買い（Dip Buy）」判定が出るか確認します。
- **テストケース 2**: 平穏なデータで実行し、「安定/レンジ」判定になることを確認します。

### 手動検証 (Manual Verification)
- 新しい検証スクリプトを実行し、テキスト出力（ダッシュボード1〜4のスコアと最終予測）が期待通りか目視で確認します。
