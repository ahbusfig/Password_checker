"""
formatter.py — Renderizado en consola: colores ANSI, barras de progreso,
               detalle por password y resumen estadístico de lotes.
"""

from __future__ import annotations

import re
import sys

from .analyzer import PasswordResult

# ── Colores ANSI ───────────────────────────────────────────────────────────

_ANSI = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "red":    "\033[91m",
    "yellow": "\033[93m",
    "green":  "\033[92m",
    "cyan":   "\033[96m",
    "gray":   "\033[90m",
    "blue":   "\033[94m",
}

def _c(text: str, color: str) -> str:
    """Aplica color ANSI solo si stdout es una terminal."""
    if sys.stdout.isatty():
        return f"{_ANSI.get(color, '')}{text}{_ANSI['reset']}"
    return text

# ── Helpers ────────────────────────────────────────────────────────────────

_SCORE_TO_COLOR = {
    (0,  20): "red",
    (20, 40): "red",
    (40, 60): "yellow",
    (60, 80): "cyan",
    (80, 101): "green",
}

def _score_color(score: int) -> str:
    for (lo, hi), color in _SCORE_TO_COLOR.items():
        if lo <= score < hi:
            return color
    return "green"

def _score_bar(score: int, width: int = 30) -> str:
    filled = int(score / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    return _c(bar, _score_color(score))

def mask_password(pwd: str) -> str:
    """Enmascara todos los caracteres excepto el primero y el último."""
    if len(pwd) <= 2:
        return "*" * len(pwd)
    return pwd[0] + "*" * (len(pwd) - 2) + pwd[-1]

def strip_ansi(text: str) -> str:
    """Elimina códigos de escape ANSI (para guardar en archivo)."""
    return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub("", text)

# ── Check labels ───────────────────────────────────────────────────────────

_CHECK_LABELS: dict[str, str] = {
    "min_length":        "Longitud mínima (≥8)",
    "good_length":       "Longitud recomendada (≥12)",
    "has_uppercase":     "Contiene mayúsculas",
    "has_lowercase":     "Contiene minúsculas",
    "has_digit":         "Contiene números",
    "has_symbol":        "Contiene símbolos",
    "not_common":        "No es contraseña común",
    "no_repeating":      "Sin repeticiones (aaa, 111...)",
    "no_sequential":     "Sin secuencias (abc, 123...)",
    "no_keyboard_walk":  "Sin patrones de teclado",
}

# ── Formateo de un resultado individual ───────────────────────────────────

def format_result(
    r: PasswordResult,
    show_password: bool = False,
    index: int | None = None,
) -> str:
    lines = []
    sep   = "─" * 52

    prefix      = f"[{index}] " if index is not None else ""
    pwd_display = r.password if show_password else mask_password(r.password)
    lvl_color   = _score_color(r.score)

    lines.append(_c(sep, "gray"))
    lines.append(_c(f"{prefix}Password: ", "bold") + _c(pwd_display, "cyan"))
    lines.append(f"Longitud : {r.length} caracteres")
    lines.append(f"Entropía : {r.entropy} bits")
    lines.append(
        f"Nivel    : {_c(r.level, lvl_color)}  ({r.score}/100)"
    )
    lines.append(
        f"Fuerza   : [{_score_bar(r.score)}] {r.score}%"
    )

    lines.append("")
    lines.append(_c("Checks:", "bold"))
    for key, label in _CHECK_LABELS.items():
        icon = _c("✔", "green") if r.checks.get(key) else _c("✘", "red")
        lines.append(f"  {icon}  {label}")

    clean_issues = [i for i in r.issues if i != "✅ Sin problemas detectados"]
    if clean_issues:
        lines.append("")
        lines.append(_c("Problemas:", "bold"))
        for issue in clean_issues:
            lines.append(f"  {issue}")

    if r.suggestions:
        lines.append("")
        lines.append(_c("Sugerencias:", "bold"))
        for sug in r.suggestions:
            lines.append(f"  → {sug}")

    return "\n".join(lines)

# ── Resumen de lote ────────────────────────────────────────────────────────

_LEVEL_SCORE: dict[str, int] = {
    "Muy débil": 10, "Débil": 30, "Moderada": 50, "Fuerte": 70, "Muy fuerte": 90,
}

def format_summary(results: list[PasswordResult]) -> str:
    total = len(results)
    if total == 0:
        return _c("No hay resultados para resumir.", "yellow")

    levels: dict[str, int] = {k: 0 for k in _LEVEL_SCORE}
    for r in results:
        levels[r.level] += 1

    avg_score   = sum(r.score   for r in results) / total
    avg_entropy = sum(r.entropy for r in results) / total

    lines = [
        "",
        _c("═" * 52, "cyan"),
        _c("  RESUMEN DEL ANÁLISIS", "bold"),
        _c("═" * 52, "cyan"),
        f"  Total passwords analizadas : {total}",
        f"  Score promedio             : {avg_score:.1f}/100",
        f"  Entropía promedio          : {avg_entropy:.1f} bits",
        "",
        _c("  Distribución por nivel:", "bold"),
    ]

    for level, count in levels.items():
        pct       = count / total * 100
        bar       = "█" * int(pct / 5)
        lvl_color = _score_color(_LEVEL_SCORE[level])
        lines.append(
            f"  {_c(f'{level:<12}', lvl_color)} {count:4d} ({pct:5.1f}%)  {_c(bar, lvl_color)}"
        )

    # Top 3 más débiles
    weakest = sorted(results, key=lambda x: x.score)[:3]
    lines.append("")
    lines.append(_c("  Las 3 passwords más débiles:", "bold"))
    for r in weakest:
        lines.append(
            f"  → {mask_password(r.password):<20s}  score: {r.score:3d}  ({r.level})"
        )

    lines.append(_c("═" * 52, "cyan"))
    return "\n".join(lines)

# ── Banner ─────────────────────────────────────────────────────────────────
BANNER = _c("""
╔══════════════════════════════════════════════╗
║        PASSWORD STRENGTH CHECKER v1.0       ║
║     Defensive Security · Portfolio Tool     ║
╚══════════════════════════════════════════════╝
""", "cyan")
