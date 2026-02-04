"""Metal Analyzer パッケージ。

貴金属（ゴールドなど）の市場価格を分析し、トレンド判定や
特定のチャートパターンを検知するための機能を提供します。
"""

__version__ = '0.0.2'

from .core.analyzer import MetalAnalyzer
from . import indicators
from . import patterns
from . import models

# 短期トレンド分析モデルの直接インポート
from .models.short_trend_predictor import analyze_short_trend

# 後方互換性のためのエイリアス
GoldAnalyzer = MetalAnalyzer

__all__ = ['MetalAnalyzer', 'GoldAnalyzer', 'indicators', 'patterns', 'models', 'analyze_short_trend']
