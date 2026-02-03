# Metal Analyzer

貴金属（ゴールド等）の市場価格を高度に分析し、トレンド判定や特定のチャートパターン（ダブルトップ等）を検知するためのPythonライブラリです。

## 特徴

特徴|説明
--|--
独自の高精度トレンド分析|4つの主要指標（長期トレンド、モメンタム、ボラティリティ加速、センチメント）を元に暴落や急騰を予測。
マルチタイムフレーム対応|月・週・日・4時・1時・15分足の計6種類の時間足を作成。EMA 20/50/200とボリンジャーバンドを描画し、トレンドをわかりやすく可視化。

## アルゴリズム実装の対比検証

「崩落の予兆」や「Wトップ形成からの急落」といったプロトレーダーの分析手法を、本ライブラリがどのようにコード化しているかの対比です。

| 動画の解説ポイント (Video Technique) | 実装内容 (Current Implementation) |
| :--- | :--- |
| **Wトップ（ダブルトップ）の形成** | `detect_double_top` 関数で2つのピークを検出し、価格差3%以内でダブルトップと認定（`scipy.signal.find_peaks`利用）。 |
| **ネックライン（重要な節目）割れ** | 2つのピーク間の最安値（ネックライン）を算出し、現在価格がそれを下回った場合に「検知(True)」を返します。 |
| **「買い全員焼かれる」 (強い売り)** | ネックライン割れを検知すると、センチメントスコアを**「-5 (暴落確定)」**に設定し、強力な売りバイアスをかけます。 |
| **崩落の予兆 (ボラティリティ加速)** | ダッシュボード3で、直近の値幅が過去平均の1.5倍を超えた場合に「加速中」と判定し、最終スコアを**1.5倍に増幅**させます。 |
| **大暴落シナリオ** | 総合スコアが「-6」以下となった場合、最終予測として **`⚠️ 大暴落加速 (Great Crash Acceleration)`** を出力します。 |

## 過去の急変動局面での予測精度（バックテスト結果）

直近の価格変動が大きかった局面に対するバックテスト結果です。
「暴落」に関しては極めて高い精度で予兆を検知できていますが、急落後の「V字急騰」については課題が残っています。

| 日付 | 実際の動き | 予測結果 | 判定 |
| :--- | :--- | :--- | :--- |
| **2025-10-20** | 翌日 -5.7% 急落 | **⚠️ 大暴落加速** (Great Crash) | ⭕ **成功** |
| **2025-12-26** | 翌週 -4.5% 下落 | **続落注意** (Caution) | ⭕ **概ね成功** |
| **2026-01-29** | 翌日 -11.3% 大暴落 | **⚠️ 大暴落加速** (Great Crash) | ⭕ **大成功** |
| **2026-02-02** | 翌日 +6.9% 急騰 | **続落注意** (Caution) | ❌ **失敗** |


## インストール

```bash
cd metal-analyzer
pip install .
```

## クイックスタート：Pythonコードでの利用

デモスクリプト以外にも、ライブラリの各コンポーネントをPythonコードから直接呼び出して、独自の分析フローを構築できます。

```python
from metal_analyzer import MetalAnalyzer
import yfinance as yf

# 1. インスタンスの初期化
analyzer = MetalAnalyzer(ticker="GC=F")

# 2. データの取得と追加（Yahoo Finance等を利用）
daily_df = yf.download("GC=F", period="2y", interval="1d")
h1_df = yf.download("GC=F", period="2mo", interval="1h")

analyzer.add_timeframe_data("Daily", daily_df)
analyzer.add_timeframe_data("1h", h1_df)

# 3. 様々な分析機能の実行

# A. 高度なトレンド予測（4つのダッシュボード）
result_adv = analyzer.analyze_advanced_trend()
print(f"予測: {result_adv['final_prediction']}")

# B. トップダウン判定（日足と1時間足の組み合わせ）
# 内部的に analyze_top_down 関数が呼び出されます
from metal_analyzer.models import analyze_top_down
td_res = analyze_top_down(daily_df, h1_df)
print(f"短期/長期判定: {td_res['prediction']}")

# C. チャートパターン検知（ダブルトップ）
detected, details = analyzer.detect_double_top()
if detected:
    print(f"パターン検知: {details}")

# D. エントリーシグナル判定
from metal_analyzer.models import determine_entry_signals
signal = determine_entry_signals(h1_df)
print(f"売買シグナル: {signal} (1:Buy, -1:Sell, 0:Wait)")

# 4. チャートの生成
# EMA 20/50/200 とボリンジャーバンドが自動で描画されます
analyzer.plot_candlestick("1h", filename="my_analysis.png", title="Gold 1H Analysis")
```

---

## 使い方：3つのメイン・デモ

当ライブラリの全機能を体験するための3つのデモスクリプトが `examples/` フォルダに用意されています。

### 1. 総合分析デモ (`examples/demo.py`)
最新の市場データを用いて、全時間足のチャート生成と高度トレンド予測を一度に実行します。

#### 実行結果（標準出力）
```text
=== Metal Analyzer 総合分析デモ ===
[1] データ取得およびチャート生成中...
[2] 高度なトレンド分析
==================================================
 ■高精度ゴールド分析ダッシュボード
==================================================
【長期トレンド： トレンド転換点/混在
【モメンタム：   下落の勢い強い
【加速/ボラ：    安定
【センチメント】 レンジ内
--------------------------------------------------
 最終予測: 続落注意
 リスク:   中
 コメント: 下落バイアスが強いですが、本格的な加速（暴落）にはまだ至っていません。
==================================================
```

#### 出力チャート（6時間足）
<details>
<summary>クリックして全時間足チャート（6枚）を表示</summary>

- **月足 (Monthly)**
  ![Monthly](examples/outputs/candles/chart_monthly.png)
- **週足 (Weekly)**
  ![Weekly](examples/outputs/candles/chart_weekly.png)
- **日足 (Daily)**
  ![Daily](examples/outputs/candles/chart_daily.png)
- **4時間足 (4H)**
  ![4H](examples/outputs/candles/chart_4h.png)
- **1時間足 (1H)**
  ![1H](examples/outputs/candles/chart_1h.png)
- **15分足 (15M)**
  ![15M](examples/outputs/candles/chart_15m.png)

</details>

---

### 2. 暴落加速シミュレーション (`examples/demo-20260130.py`)
歴史的な暴落局面（2026年1月30日）を再現し、ダブルトップのネックライン割れと下落加速シグナルを検知します。

#### 実行結果（標準出力）
```text
==================================================
 ■高精度ゴールド分析ダッシュボード
==================================================
【長期トレンド： トレンド転換点/混在
【モメンタム：   下落の勢い強い
【加速/ボラ：    安定
【センチメント】 重要ライン割れ (暴落の危険大)
--------------------------------------------------
 最終予測: ⚠️ 大暴落加速 (Great Crash Acceleration)
 リスク:   極めて高い
 コメント: 重要ラインを割り込み、ボラティリティが急増しています。トレンドの底が見えません。
==================================================
```

#### 出力チャート（6時間足）
<details>
<summary>クリックして全時間足チャート（6枚）を表示</summary>

- **月足 (Monthly)**
  ![Monthly](examples/outputs/candles/20260130_chart_monthly.png)
- **週足 (Weekly)**
  ![Weekly](examples/outputs/candles/20260130_chart_weekly.png)
- **日足 (Daily)**
  ![Daily](examples/outputs/candles/20260130_chart_daily.png)
- **4時間足 (4H)**
  ![4H](examples/outputs/candles/20260130_chart_4h.png)
- **1時間足 (1H)**
  ![1H](examples/outputs/candles/20260130_chart_1h.png)
- **15分足 (15M)**
  ![15M](examples/outputs/candles/20260130_chart_15m.png)

</details>

---

### 3. 上昇トレンド転換シミュレーション (`examples/demo-20251230.py`)
レンジ相場から上昇に転じる局面（2025年12月30日）を再現し、底堅さの判定を検証します。

#### 実行結果（標準出力）
```text
==================================================
 ■高精度ゴールド分析ダッシュボード
==================================================
【長期トレンド： トレンド転換点/混在
【モメンタム：   穏やか
【加速/ボラ：    安定
【センチメント】 レンジ内
--------------------------------------------------
 最終予測: 底堅い/反発
 リスク:   低
 コメント: 買い圧力が優勢、またはレンジ下限での反発が見られます。
==================================================
```

#### 出力チャート（6時間足）
<details>
<summary>クリックして全時間足チャート（6枚）を表示</summary>

- **月足 (Monthly)**
  ![Monthly](examples/outputs/candles/20251230_chart_monthly.png)
- **週足 (Weekly)**
  ![Weekly](examples/outputs/candles/20251230_chart_weekly.png)
- **日足 (Daily)**
  ![Daily](examples/outputs/candles/20251230_chart_daily.png)
- **4時間足 (4H)**
  ![4H](examples/outputs/candles/20251230_chart_4h.png)
- **1時間足 (1H)**
  ![1H](examples/outputs/candles/20251230_chart_1h.png)
- **15分足 (15M)**
  ![15M](examples/outputs/candles/20251230_chart_15m.png)

</details>

---

## プロジェクト構成

各ファイルの詳細な役割を以下に示します。

| フォルダ | ファイル | 説明 |
| :--- | :--- | :--- |
| `core/` | [`analyzer.py`](metal_analyzer/core/analyzer.py) | メインクラス `MetalAnalyzer` 。データの管理、分析の実行、プロットの指示を統括。 |
| `indicators/` | [`sma.py`](metal_analyzer/indicators/sma.py) | 移動平均線（SMA, EMA）の計算アルゴリズム。 |
| | [`bollinger_bands.py`](metal_analyzer/indicators/bollinger_bands.py) | ボリンジャーバンドの計算アルゴリズム。 |
| | [`rsi.py`](metal_analyzer/indicators/rsi.py) | 相対力指数（RSI）の計算アルゴリズム。 |
| `patterns/` | [`double_top.py`](metal_analyzer/patterns/double_top.py) | SciPyを用いたダブルトップ（Mトップ）検知ロジック。 |
| `models/` | [`advanced_predictor.py`](metal_analyzer/models/advanced_predictor.py) | 高精度トレンド予測エンジン。 |
| | [`top_down.py`](metal_analyzer/models/top_down.py) | マルチタイムフレーム分析ロジック。 |
| | [`signal_entry.py`](metal_analyzer/models/signal_entry.py) | エントリー・エグジット判定。 |
| `examples/` | [`demo.py`](examples/demo.py) | 総合分析デモスクリプト。 |
| | [`demo-20260130.py`](examples/demo-20260130.py) | 暴落局面シミュレーション。 |
| | [`demo-20251230.py`](examples/demo-20251230.py) | トレンド転換シミュレーション。 |
