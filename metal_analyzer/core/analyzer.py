import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from ..indicators import calculate_sma, calculate_rsi
from ..patterns import detect_double_top
from ..models import analyze_top_down as run_top_down, determine_entry_signals

class MetalAnalyzer:
    """貴金属価格を分析するためのメインクラス。

    Attributes:
        ticker (str): Yahoo Financeのティッカーシンボル。
        data (pd.DataFrame): 分析対象のメインデータ。
        daily_data (pd.DataFrame): トップダウン分析用の日足データ。
        hourly_data (pd.DataFrame): トップダウン分析用の1時間足データ。
    """

    def __init__(self, ticker="GC=F"):
        """MetalAnalyzerを初期化する。

        Args:
            ticker (str): Yahoo Financeのティッカーシンボル。
        """
        self.ticker = ticker
        self.data = None
        self.daily_data = None
        self.hourly_data = None

    def set_data(self, data):
        """分析対象のデータをセットする。

        Args:
            data (pd.DataFrame): 分析に使用するメインの時系列データ。
        """
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        self.data = data

    def set_multi_timeframe_data(self, daily_data, hourly_data):
        """トップダウン分析用のデータをセットする。

        Args:
            daily_data (pd.DataFrame): 日足の価格データ。
            hourly_data (pd.DataFrame): 1時間足の価格データ。
        """
        if isinstance(daily_data.columns, pd.MultiIndex):
            daily_data.columns = daily_data.columns.get_level_values(0)
        if isinstance(hourly_data.columns, pd.MultiIndex):
            hourly_data.columns = hourly_data.columns.get_level_values(0)
            
        self.daily_data = daily_data
        self.hourly_data = hourly_data

    def calculate_sma(self, window=20):
        """単純移動平均(SMA)を計算し、データフレームに追加する。

        Args:
            window (int): 平均を取る期間。
        """
        if self.data is not None:
            self.data[f'SMA_{window}'] = calculate_sma(self.data, window)

    def calculate_rsi(self, window=14):
        """RSI(Relative Strength Index)を計算し、データフレームに追加する。

        Args:
            window (int): RSIの計算期間。
        """
        if self.data is not None:
            self.data['RSI'] = calculate_rsi(self.data, window)

    def analyze_entry_points(self):
        """SMAクロスとRSIに基づいてエントリーシグナルを判定する。"""
        if self.data is not None:
            self.data['Signal'] = determine_entry_signals(self.data)

    def detect_double_top(self, threshold=0.03, lookback=100):
        """ダブルトップパターンの検知を実行する。

        Args:
            threshold (float): ピーク間の価格差許容率。
            lookback (int): 探索対象とする過去のデータ数。

        Returns:
            tuple: (is_detected, details) の結果。
        """
        return detect_double_top(self.hourly_data, threshold, lookback)

    def analyze_top_down(self):
        """マルチタイムフレームでのトップダウン分析を実行し、結果を表示する。

        Returns:
            str: 最終的な判定シグナル。
        """
        if self.daily_data is None or self.hourly_data is None:
            print("データがありません。")
            return
            
        signal, prediction, d_trend, h_trend, h_rsi = run_top_down(self.daily_data, self.hourly_data)
        
        print("\n--- トップダウン分析結果 ---")
        print(f"【日足 (長期)】 トレンド: {d_trend}")
        print(f"【1時間足 (短期)】 状態: {h_trend}, RSI: {h_rsi:.2f}")
        print(f"\n★ 判定シグナル: {signal}")
        print(f"★ 短期予測コメント: {prediction}")
        print("------------------------------------------\n")
        
        return signal

    def plot_data(self, filename="analysis_plot.png"):
        """分析結果を可視化したグラフを保存する。

        Args:
            filename (str): 保存するファイル名またはパス。
        """
        if self.data is None or self.data.empty:
            print("データがありません。")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})

        # 価格とSMAのプロット
        ax1.plot(self.data.index, self.data['Close'], label='Close Price', alpha=0.5)
        
        for col in self.data.columns:
            if 'SMA' in col:
                ax1.plot(self.data.index, self.data[col], label=col)
        
        ax1.set_title(f'{self.ticker} Price Analysis')
        ax1.set_ylabel('Price (USD)')
        
        # 売買シグナルのプロット
        if 'Signal' in self.data.columns:
            buy_signals = self.data[self.data['Signal'] == 1]
            ax1.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', label='Buy Signal', s=100, zorder=5)
            
            sell_signals = self.data[self.data['Signal'] == -1]
            ax1.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', label='Sell Signal', s=100, zorder=5)
            
        ax1.legend()
        ax1.grid(True)

        # RSIのプロット
        if 'RSI' in self.data.columns:
            ax2.plot(self.data.index, self.data['RSI'], label='RSI', color='purple')
            ax2.axhline(70, linestyle='--', alpha=0.5, color='red')
            ax2.axhline(30, linestyle='--', alpha=0.5, color='green')
            ax2.set_title('Relative Strength Index (RSI)')
            ax2.set_ylabel('RSI')
            ax2.set_ylim(0, 100)
            ax2.legend()
            ax2.grid(True)

        plt.tight_layout()
        
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        plt.savefig(filename)
        print(f"グラフを {filename} として保存しました。")
        plt.close()
