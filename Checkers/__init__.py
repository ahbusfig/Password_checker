"""
checker — Password Strength Checker package.

API pública:
    from checker import analyze, analyze_many, PasswordResult
"""

from .analyzer import PasswordResult, analyze, analyze_many

__all__ = ["analyze", "analyze_many", "PasswordResult"]
