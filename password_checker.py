#!/usr/bin/env python3
"""
password_checker.py — CLI entrypoint (thin wrapper).

Toda la lógica vive en Checkers/. Este módulo solo maneja:
  - Argumentos CLI (argparse)
  - Lectura de input (inline / archivo)
  - Escritura de output (stdout / archivo)

Uso:
  python password_checker.py -p "MiPassword123!"
  python password_checker.py -f passwords.txt
  python password_checker.py -f passwords.txt -o report.txt
  python password_checker.py -f passwords.txt --show-passwords
"""
import argparse
import sys
from pathlib import Path

from Checkers import analyze, analyze_many
from Checkers.formatter import *

# ── CLI ────────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="password_checker",
        description="Evalúa la fortaleza de contraseñas (longitud, entropía, patrones).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python password_checker.py -p "MiS3cur3P@ss!"
  python password_checker.py -f passwords.txt
  python password_checker.py -f passwords.txt -o report.txt --show-passwords
        """,
    )
    parser.add_argument(
        "-p", "--password",
        metavar="PWD",
        help="Contraseña a analizar directamente",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Archivo .txt con una contraseña por línea",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Guardar el reporte en un archivo de texto",
    )
    parser.add_argument(
        "--show-passwords",
        action="store_true",
        help="Mostrar contraseñas en claro (por defecto se enmascaran)",
    )
    return parser

# ── Lógica de cada modo ────────────────────────────────────────────────────
def run_single(password: str) -> list[str]:
    """Analiza una contraseña individual."""
    result = analyze(password)
    out    = format_result(result, show_password=True)
    print(out)
    return [out]

def run_file(args: argparse.Namespace) -> list[str]:
    """Analiza un archivo con varias contraseñas."""
    path = Path(args.file)
    if not path.exists():
        print(f"Error: no se encontró '{args.file}'", file=sys.stderr)
        sys.exit(1)

    passwords = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not passwords:
        print("El archivo está vacío o sin líneas válidas.", file=sys.stderr)
        sys.exit(1)

    print(f"Analizando {len(passwords)} contraseñas de '{args.file}'...\n")

    results = analyze_many(passwords)
    output  = []

    for i, result in enumerate(results, 1):
        out = format_result(result, show_password=args.show_passwords, index=i)
        print(out)
        output.append(out)

    summary = format_summary(results)
    print(summary)
    output.append(summary)
    return output

# ── Helpers ────────────────────────────────────────────────────────────────
def _save_report(lines: list[str], path: str) -> None:
    """Guarda reporte limpio (sin ANSI) en archivo."""
    clean = strip_ansi("\n".join(lines))
    Path(path).write_text(clean, encoding="utf-8")
    print(f"\n✔ Reporte guardado en: {path}")

# ── Main ───────────────────────────────────────────────────────────────────
def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    print(BANNER)
    output: list[str] = []

    if args.password:
        output = run_single(args.password)
    elif args.file:
        output = run_file(args)
    else:
        parser.print_usage()

    if args.output and output:
        _save_report(output, args.output)

if __name__ == "__main__":
    main()