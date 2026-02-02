from .core.analyzer import MetalAnalyzer
from . import indicators
from . import patterns
from . import models

# 後方互換性のためのエイリアス
GoldAnalyzer = MetalAnalyzer

__all__ = ['MetalAnalyzer', 'GoldAnalyzer', 'indicators', 'patterns', 'models']
