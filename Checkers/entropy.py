"""
entropy.py — Cálculo de entropía de contraseñas.

Entropía (bits) = log2(tamaño_charset ^ longitud)
                = longitud * log2(tamaño_charset)

En el contexto de contraseñas, entropía mide cuántas combinaciones posibles tiene una contraseña 
o sea, qué tan difícil es adivinarla por fuerza bruta.

El charset se infiere de los caracteres reales presentes en la password.
"""
import math
import re

# Tamaños de charset por categoría
_CHARSET_LOWERCASE = 26   # a-z
_CHARSET_UPPERCASE = 26   # A-Z
_CHARSET_DIGITS    = 10   # 0-9
_CHARSET_SYMBOLS   = 32   # símbolos estándar de teclado (~printable ASCII - alfanum)


def detect_charset_size(password: str) -> int:
    """
    Devuelve el tamaño del espacio de caracteres usado en la password.
    Suma los rangos de cada categoría presente.
    """
    size = 0
    if re.search(r'[a-z]', password):
        size += _CHARSET_LOWERCASE
    if re.search(r'[A-Z]', password):
        size += _CHARSET_UPPERCASE
    if re.search(r'[0-9]', password):
        size += _CHARSET_DIGITS
    if re.search(r'[^a-zA-Z0-9]', password):
        size += _CHARSET_SYMBOLS
    return size

def calculate_entropy(password: str) -> float:
    """
    Calcula la entropía en bits de una password.
    Retorna 0.0 si la password está vacía o el charset es 0.

    Referencia: NIST SP 800-63B — la entropía basada en longitud
    y variedad de caracteres es una métrica estándar de fortaleza.
    """
    if not password:
        return 0.0
    charset_size = detect_charset_size(password)
    if charset_size == 0:
        return 0.0
    return round(len(password) * math.log2(charset_size), 1)

def entropy_label(bits: float) -> str:
    """Clasificación cualitativa de la entropía."""
    if bits < 28:  return "Muy baja"
    if bits < 36:  return "Baja"
    if bits < 60:  return "Aceptable"
    if bits < 80:  return "Alta"
    return "Muy alta"
