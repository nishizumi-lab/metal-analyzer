from .core.analyzer import MetalAnalyzer
from . import indicators
from . import patterns
from . import models

# 高度な予測モデルの直接インポート
from .models.advanced_predictor import analyze_advanced_trend

# 後方互換性のためのエイリアス
GoldAnalyzer = MetalAnalyzer

__all__ = ['MetalAnalyzer', 'GoldAnalyzer', 'indicators', 'patterns', 'models', 'analyze_advanced_trend']
