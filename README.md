# 🔐 Password Strength Checker CLI

Herramienta de línea de comandos para evaluar la fortaleza de contraseñas. Analiza longitud, entropía, patrones débiles y compara contra una lista de contraseñas comunes — sin dependencias externas.

## ¿Cómo funciona?

Cada contraseña pasa por 10 checks independientes y recibe un score de 0 a 100:

| Score | Nivel |
|-------|-------|
| 0 – 19 | Muy débil |
| 20 – 39 | Débil |
| 40 – 59 | Moderada |
| 60 – 79 | Fuerte |
| 80 – 100 | Muy fuerte |

## Checks implementados

| Check | Descripción |
|-------|-------------|
| Longitud mínima | Al menos 8 caracteres |
| Longitud recomendada | 12 o más caracteres |
| Mayúsculas | Contiene letras A-Z |
| Minúsculas | Contiene letras a-z |
| Dígitos | Contiene números 0-9 |
| Símbolos | Contiene caracteres especiales |
| Contraseña común | Comparación contra wordlist (con soporte leet-speak) |
| Caracteres repetidos | Detecta patrones como `aaa`, `111` |
| Secuencias | Detecta `abcde`, `12345` y similares |
| Patrones de teclado | Detecta `qwerty`, `asdf`, `zxcv` |

## Estructura del proyecto
```
Password_checker/
├── password_checker.py        # Entrada CLI — argparse, modos inline y batch
├── Checkers/
│   ├── __init__.py
│   ├── analyzer.py            # Lógica central de análisis y scoring
│   ├── entropy.py             # Cálculo de entropía
│   ├── patterns.py            # Patrones débiles y carga de wordlist
│   └── formatter.py           # Output en terminal con colores
├── wordlists/
│   └── common_passwords.txt   # Lista de contraseñas comunes
├── tests/
├── passwords_test.txt         # Contraseñas de ejemplo para pruebas
├── requirements.txt
└── README.md
```

## Uso
```bash
# Contraseña directa
python password_checker.py -p "MiPassword123!"

# Fichero con varias contraseñas (una por línea)
python password_checker.py -f passwords.txt

# Guardar reporte en fichero
python password_checker.py -f passwords.txt -o report.txt

# Mostrar contraseñas en claro (por defecto se enmascaran)
python password_checker.py -f passwords.txt --show-passwords
```

## Wordlist

El checker compara automáticamente cada contraseña contra `wordlists/common_passwords.txt`. Si el fichero no existe, usa un fallback embebido con las contraseñas más comunes.

La comparación incluye detección de **leet-speak** — `p@ssw0rd` se detecta como variante de `password`.

## Requisitos

Python 3.10 o superior. Sin dependencias externas.

## Limitaciones conocidas

- El scoring es heurístico — una contraseña puede tener score alto y aun así ser predecible si no está en el wordlist.
- La detección de leet-speak cubre sustituciones básicas (`@` → `a`, `0` → `o`, `1` → `i`...). Combinaciones complejas pueden no detectarse.
- No evalúa contexto — no sabe si la contraseña contiene el nombre del usuario o la fecha de nacimiento.

## Posibles mejoras

- Integración con HaveIBeenPwned API para verificar si la contraseña ha sido filtrada
- Detección de contraseñas basadas en fechas (`01011990`, `1990enero`)
- Soporte para exportar reporte en JSON