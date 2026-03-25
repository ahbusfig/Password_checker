"""
analyzer.py — Lógica central de análisis y scoring de contraseñas.

Devuelve un dataclass PasswordResult con todos los resultados.
No tiene dependencias de UI ni de formateo.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .entropy import calculate_entropy
from .patterns import *

# ── Resultado del análisis ─────────────────────────────────────────────────
@dataclass
class PasswordResult:
    password:    str
    length:      int
    entropy:     float
    score:       int
    level:       str
    checks:      dict[str, bool] = field(default_factory=dict)
    issues:      list[str]       = field(default_factory=list)
    suggestions: list[str]       = field(default_factory=list)

# ── Etiquetas de nivel ─────────────────────────────────────────────────────
def _level_from_score(score: int) -> str:
    if score < 20: return "Muy débil"
    if score < 40: return "Débil"
    if score < 60: return "Moderada"
    if score < 80: return "Fuerte"
    return "Muy fuerte"

# ── Checks ─────────────────────────────────────────────────────────────────
def _run_checks(password: str, common: frozenset[str]) -> dict[str, bool]:
    pwd_lower = password.lower()
    pwd_leet  = pwd_lower.translate(LEET_TABLE)

    return {
        "min_length":        len(password) >= 8,
        "good_length":       len(password) >= 12,
        "has_uppercase":     bool(re.search(r'[A-Z]', password)),
        "has_lowercase":     bool(re.search(r'[a-z]', password)),
        "has_digit":         bool(re.search(r'[0-9]', password)),
        "has_symbol":        bool(re.search(r'[^a-zA-Z0-9]', password)),
        "not_common":        pwd_lower not in common and pwd_leet not in common,
        "no_repeating":      not bool(re.search(r'(.)\1{2,}', password)),
        "no_sequential":     not any(
                                 pwd_lower[i:i+4] in seq
                                 for seq in SEQUENTIAL_PATTERNS
                                 for i in range(max(0, len(pwd_lower) - 3))
                             ),
        "no_keyboard_walk":  not any(walk in pwd_lower for walk in KEYBOARD_WALKS),
    }

# ── Scoring ────────────────────────────────────────────────────────────────
def _compute_score(password: str, checks: dict[str, bool], entropy: float) -> int:
    score = 0

    n = len(password)
    if n >= 6:  score += 5
    if n >= 8:  score += 10
    if n >= 12: score += 15
    if n >= 16: score += 10
    if n >= 20: score += 5

    if checks["has_uppercase"]: score += 10
    if checks["has_lowercase"]: score += 10
    if checks["has_digit"]:     score += 10
    if checks["has_symbol"]:    score += 15

    if entropy >= 40: score += 5
    if entropy >= 60: score += 10
    if entropy >= 80: score += 10

    if not checks["not_common"]:       score -= 40
    if not checks["no_repeating"]:     score -= 10
    if not checks["no_sequential"]:    score -= 10
    if not checks["no_keyboard_walk"]: score -= 10
    if n < 8:                          score -= 10

    return max(0, min(100, score))

# ── Issues y sugerencias ───────────────────────────────────────────────────
def _build_feedback(
    password: str,
    checks: dict[str, bool],
) -> tuple[list[str], list[str]]:
    issues: list[str]      = []
    suggestions: list[str] = []

    if not checks["not_common"]:
        issues.append("❌ Password en lista de contraseñas comunes")
        suggestions.append("Usa una contraseña única, no palabras de diccionario")

    if not checks["min_length"]:
        issues.append(f"❌ Muy corta ({len(password)} caracteres, mínimo 8)")
        suggestions.append("Usa al menos 8 caracteres (recomendado 12+)")
    elif not checks["good_length"]:
        issues.append(f"⚠️  Longitud aceptable ({len(password)} chars), pero 12+ es mejor")

    if not checks["has_uppercase"]:
        issues.append("⚠️  Sin mayúsculas")
        suggestions.append("Añade letras mayúsculas (A-Z)")

    if not checks["has_lowercase"]:
        issues.append("⚠️  Sin minúsculas")
        suggestions.append("Añade letras minúsculas (a-z)")

    if not checks["has_digit"]:
        issues.append("⚠️  Sin números")
        suggestions.append("Añade dígitos (0-9)")

    if not checks["has_symbol"]:
        issues.append("⚠️  Sin símbolos especiales")
        suggestions.append("Añade símbolos: ! @ # $ % ^ & * ( ) _ + - = [ ] { }")

    if not checks["no_repeating"]:
        issues.append("⚠️  Caracteres repetidos consecutivos (ej: aaa, 111)")

    if not checks["no_sequential"]:
        issues.append("⚠️  Secuencia detectada (ej: abcde, 12345)")

    if not checks["no_keyboard_walk"]:
        issues.append("⚠️  Patrón de teclado detectado (ej: qwerty, asdf)")

    if not issues:
        issues.append("✅ Sin problemas detectados")

    return issues, suggestions

# ── API pública ────────────────────────────────────────────────────────────
def analyze(password: str) -> PasswordResult:
    """Analiza una contraseña y devuelve un PasswordResult completo."""
    common  = load_common_passwords()
    entropy = calculate_entropy(password)
    checks  = _run_checks(password, common)
    score   = _compute_score(password, checks, entropy)
    issues, suggestions = _build_feedback(password, checks)

    return PasswordResult(
        password    = password,
        length      = len(password),
        entropy     = entropy,
        score       = score,
        level       = _level_from_score(score),
        checks      = checks,
        issues      = issues,
        suggestions = suggestions,
    )

def analyze_many(passwords: list[str]) -> list[PasswordResult]:
    """Analiza una lista de contraseñas. Reutiliza el mismo wordlist."""
    common = load_common_passwords()

    results = []
    for pwd in passwords:
        entropy = calculate_entropy(pwd)
        checks  = _run_checks(pwd, common)
        score   = _compute_score(pwd, checks, entropy)
        issues, suggestions = _build_feedback(pwd, checks)
        results.append(PasswordResult(
            password    = pwd,
            length      = len(pwd),
            entropy     = entropy,
            score       = score,
            level       = _level_from_score(score),
            checks      = checks,
            issues      = issues,
            suggestions = suggestions,
        ))
    return results