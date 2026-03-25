"""
patterns.py — Listas de patrones débiles y passwords comunes.
Se cargan desde wordlists/common_passwords.txt si existe;
si no, se usa el fallback embebido.
"""
from pathlib import Path

# ── Fallback embebido (top passwords más comunes) ──────────────────────────
_COMMON_FALLBACK = {
    "123456", "password", "123456789", "12345678", "12345", "1234567",
    "password1", "1234567890", "123123", "000000", "iloveyou", "1234",
    "1q2w3e4r5t", "qwerty", "abc123", "qwerty123", "1q2w3e4r",
    "admin", "letmein", "welcome", "monkey", "dragon", "master",
    "sunshine", "princess", "football", "shadow", "superman", "michael",
    "jessica", "login", "passw0rd", "starwars", "123321", "666666",
    "654321", "112233", "1qaz2wsx", "123qwe", "zxcvbnm", "password123",
    "trustno1", "baseball", "soccer", "batman", "access", "mustang",
    "hunter2", "hunter", "andrew", "thomas", "robert", "jordan",
    "harley", "ranger", "iwantu", "test", "temp", "guest",
    "changeme", "pass", "pass1", "pass12", "pass123", "root",
    "toor", "admin123", "administrator", "qazwsx", "1111", "11111",
    "111111", "1111111", "11111111", "0000", "00000", "000000",
    "999999", "123", "55555", "666", "7777777", "88888888",
    "987654321", "passpass", "p@ssw0rd", "p@ssword", "p@$$w0rd",
    "passw0rd!", "Password1", "Password1!", "Summer2023", "Winter2023",
    "Spring2023", "Fall2023", "Qwerty123", "Qwerty123!", "Hello123",
    "Welcome1", "Welcome1!",
}

# ── Secuencias de caracteres ───────────────────────────────────────────────
SEQUENTIAL_PATTERNS: list[str] = [
    "abcdefghijklmnopqrstuvwxyz",
    "zyxwvutsrqponmlkjihgfedcba",
    "0123456789",
    "9876543210",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
]

# ── Patrones de teclado ────────────────────────────────────────────────────
KEYBOARD_WALKS: list[str] = [
    "qwerty", "asdf", "zxcv", "1234", "4321", "!@#$",
    "qwer", "asdfgh", "zxcvb",
]

# ── Tabla leet-speak ──────────────────────────────────────────────────────
LEET_TABLE = str.maketrans("@0135", "aoies")

def load_common_passwords(wordlist_path: Path | None = None) -> frozenset[str]:
    """
    Carga la lista de passwords comunes.
    Prioridad: wordlist_path → wordlists/common_passwords.txt → fallback embebido.
    Devuelve frozenset de strings en minúsculas.
    """
    # Ruta por defecto relativa al paquete
    if wordlist_path is None:
        wordlist_path = Path(__file__).parent.parent / "wordlists" / "common_passwords.txt"

    if wordlist_path.exists():
        lines = wordlist_path.read_text(encoding="utf-8").splitlines()
        words = {line.strip().lower() for line in lines if line.strip()}
        if words:
            return frozenset(words)

    return frozenset(w.lower() for w in _COMMON_FALLBACK)