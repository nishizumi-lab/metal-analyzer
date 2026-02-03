"""貴金属価格分析のコア機能を提供するモジュール。

このモジュールは、各種時間足データの管理、テクニカル分析、およびチャート生成を
統括する MetalAnalyzer クラスを提供します。
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import mplfinance as mpf
from matplotlib.lines import Line2D
from ..indicators import calculate_sma, calculate_ema, calculate_rsi
from ..patterns import detect_double_top
from ..models import analyze_top_down as run_top_down, determine_entry_signals
from ..models.advanced_predictor import analyze_advanced_trend

class MetalAnalyzer:
    """貴金属価格を分析するためのメインクラス。

    Attributes:
        ticker (str): 分析対象のティッカーシンボル（例: "GC=F"）。
        timeframe_data (dict): 時間足をキーとし、Pandas DataFrameを値とする辞書。
        data (pd.DataFrame): 日足データ（後方互換性のために保持）。
        daily_data (pd.DataFrame): 日足データ。
        hourly_data (pd.DataFrame): 1時間足データ。
    """

    def __init__(self, ticker="GC=F"):
        """MetalAnalyzer を初期化する。

        Args:
            ticker (str): 分析対象のティッカーシンボル。デフォルトは "GC=F" (Gold)。
        """
        self.ticker = ticker
        self.timeframe_data = {}
        self.data = None
        self.daily_data = None
        self.hourly_data = None

    def _get_df(self, keys):
        """複数の候補キーから有効なデータフレームを取得する。

        Args:
            keys (list): 検索する時間足キーのリスト。

        Returns:
            pd.DataFrame or None: 見つかったデータフレーム。見つからない場合は None。
        """
        for key in keys:
            df = self.timeframe_data.get(key)
            if df is not None and not df.empty:
                return df
        return None

    def add_timeframe_data(self, timeframe, data):
        """特定の時間足のデータを追加する。

        Args:
            timeframe (str): 時間足の名称（例: "Daily", "1h"）。
            data (pd.DataFrame): OHLCVデータを含むデータフレーム。
        """
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
            
        self.timeframe_data[timeframe] = data
        
        norm_tf = timeframe.lower().replace('monthly', '1mo').replace('weekly', '1wk').replace('daily', '1d').replace('hourly', '1h')
        if norm_tf in ['1d', 'daily']:
            self.data = data
            self.daily_data = data
        elif norm_tf in ['1h', 'hourly']:
            self.hourly_data = data

    def analyze_advanced_trend(self):
        """高度なトレンド予測を実行し、結果を出力する。

        日足、4時間足、1時間足、およびチャートパターンを使用して、
        多角的な相場分析（4つのダッシュボード）を実行します。

        Returns:
            dict or None: 分析結果を含む辞書。データ不足の場合は None。
        """
        d_df = self._get_df(['Daily', '1d', '1D', 'daily'])
        if d_df is None: d_df = self.daily_data
        
        h4_df = self._get_df(['4h', '4H', '4hourly'])
        h1_df = self._get_df(['1h', '1H', 'hourly'])
        if h1_df is None: h1_df = self.hourly_data
        
        # 4時間足の補完
        if h4_df is None and h1_df is not None:
             h4_df = h1_df.resample('4h').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
             }).dropna()
             self.add_timeframe_data('4h', h4_df)

        if d_df is None or h4_df is None or h1_df is None:
            print("【警告】高度な分析には日足、4時間足、1時間足のデータが必要です。")
            return None

        # パターン情報の取得
        dt_detected, dt_details = self.detect_double_top()
        patterns = {'double_top': dt_detected}
        if dt_detected:
            try:
                import re
                match = re.search(r"ネックライン ([\d.]+)", dt_details)
                if match: patterns['neckline'] = float(match.group(1))
            except: pass

        res = analyze_advanced_trend(d_df, h4_df, h1_df, patterns=patterns)
        
        print("\n" + "="*50)
        print("   👑 高精度ゴールド分析ダッシュボード 👑")
        print("="*50)
        print(f"【長期トレンド】 {res['dashboard_1_trend']}")
        print(f"【モメンタム】   {res['dashboard_2_momentum']}")
        print(f"【加速/ボラ】    {res['dashboard_3_volatility']}")
        print(f"【センチメント】 {res['dashboard_4_sentiment']}")
        print("-" * 50)
        print(f" 🎯 最終予測: {res['final_prediction']}")
        print(f" ⚠️ リスク:   {res['risk_level']}")
        print(f" 📝 コメント: {res['comment']}")
        print("="*50 + "\n")
        
        return res

    def plot_candlestick(self, timeframe, filename=None, title=None):
        """特定の時間足のローソク足チャートを生成・保存する。

        EMA (20, 50, 200) を重畳し、ダークモードで出力します。

        Args:
            timeframe (str): 描画対象の時間足キー。
            filename (str, optional): 保存先のパス。指定しない場合は表示のみ（環境に依存）。
            title (str, optional): チャートのタイトル。
        """
        df = self.timeframe_data.get(timeframe)
        if df is None or df.empty:
            print(f"時間足 {timeframe} のデータがありません。")
            return

        for window in [20, 50, 200]:
            col_name = f'EMA_{window}'
            if col_name not in df.columns:
                df[col_name] = calculate_ema(df, window)

        plot_df = df.tail(100)
        apds = []
        if not plot_df['EMA_20'].isnull().all():
            apds.append(mpf.make_addplot(plot_df['EMA_20'], color='cyan', width=1.0))
        if not plot_df['EMA_50'].isnull().all():
            apds.append(mpf.make_addplot(plot_df['EMA_50'], color='yellow', width=1.0))
        if not plot_df['EMA_200'].isnull().all():
            apds.append(mpf.make_addplot(plot_df['EMA_200'], color='magenta', width=1.5))

        custom_style = mpf.make_mpf_style(
            base_mpf_style='charles', marketcolors=mpf.make_marketcolors(up='green', down='red', inherit=True),
            gridcolor='dimgray', facecolor='black', figcolor='black',
            rc={'text.color': 'white', 'axes.labelcolor': 'white', 'xtick.color': 'white',
                'ytick.color': 'white', 'axes.edgecolor': 'white', 'figure.titlesize': 'x-large'}
        )

        title = title or f"{self.ticker} - {timeframe} (Dark Mode)"
        if filename: os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        fig, axlist = mpf.plot(plot_df, type='candle', style=custom_style, addplot=apds, title=title, 
                 ylabel='Price', volume=True if 'Volume' in plot_df.columns else False,
                 savefig=dict(fname=filename, bbox_inches='tight') if filename else None,
                 tight_layout=True, scale_padding=1.5, figratio=(16, 9), datetime_format='%m/%d %H:%M', returnfig=True)
        
        if len(apds) > 0:
            labels = ['EMA 20', 'EMA 50', 'EMA 200'][:len(apds)]
            colors = ['cyan', 'yellow', 'magenta'][:len(apds)]
            handles = [Line2D([0], [0], color=c, lw=1.5) for c in colors]
            axlist[0].legend(handles, labels, loc='upper left', fontsize='small', facecolor='black', edgecolor='white', labelcolor='white')
            if filename: fig.savefig(filename, bbox_inches='tight', facecolor='black')

        if filename: print(f"【完了】{timeframe} チャートを保存しました: {filename}")

    def detect_double_top(self, threshold=0.03, lookback=100):
        """ダブルトップ（Mトップ）パターンを検知する。

        Args:
            threshold (float): 山の高さの許容誤差（割合）。
            lookback (int): 参照する直近のデータポイント数。

        Returns:
            tuple: (bool, str) 検知の有無と詳細メッセージ。
        """
        df = self._get_df(['1h', '1H', 'hourly'])
        if df is None: df = self.hourly_data
        return detect_double_top(df, threshold, lookback)

    def analyze_all(self, output_dir="examples/outputs/candles", prefix=""):
        """全時間足の分析とプロットを一括実行する。

        Args:
            output_dir (str): チャート画像の保存先ディレクトリ。
            prefix (str): ファイル名の接頭辞。
        """
        print(f"\n--- 総合分析およびチャート生成開始 (Prefix: {prefix}) ---")
        self.analyze_advanced_trend()
        
        for tf in list(self.timeframe_data.keys()):
            fname = os.path.join(output_dir, f"{prefix}chart_{tf.lower()}.png")
            self.plot_candlestick(tf, filename=fname)

    def calculate_ema(self, window=20, timeframe='default'):
        """指数平滑移動平均 (EMA) を計算してデータフレームに追加する。

        Args:
            window (int): 計算期間。
            timeframe (str): 対象の時間足キー。
        """
        df = self.timeframe_data.get(timeframe)
        if df is not None: df[f'EMA_{window}'] = calculate_ema(df, window)

    def calculate_sma(self, window=20, timeframe='default'):
        """単純移動平均 (SMA) を計算してデータフレームに追加する。

        Args:
            window (int): 計算期間。
            timeframe (str): 対象の時間足キー。
        """
        df = self.timeframe_data.get(timeframe)
        if df is not None: df[f'SMA_{window}'] = calculate_sma(df, window)

    def calculate_rsi(self, window=14, timeframe='default'):
        """相対力指数 (RSI) を計算してデータフレームに追加する。

        Args:
            window (int): 計算期間。
            timeframe (str): 対象の時間足キー。
        """
        df = self.timeframe_data.get(timeframe)
        if df is not None: df['RSI'] = calculate_rsi(df, window)

    def set_data(self, data):
        """日足データをセットする（互換用）。

        Args:
            data (pd.DataFrame): 日足データ。
        """
        self.add_timeframe_data('Daily', data)

    def set_multi_timeframe_data(self, d, h):
        """日足と1時間足データをセットする（互換用）。

        Args:
            d (pd.DataFrame): 日足データ。
            h (pd.DataFrame): 1時間足データ。
        """
        self.add_timeframe_data('Daily', d)
        self.add_timeframe_data('1h', h)
