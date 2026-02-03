"""チャートパターン検知ロジックを提供するパッケージ。

ダブルトップ（Mトップ）などの特定の形状を自動的に検出するアルゴリズムが含まれます。
"""

from .double_top import detect_double_top

__all__ = ['detect_double_top']
