"""Journalisation / progression (bilingue).

FR: Centraliser les messages [INFO]/[WARN]/[DBG] pour éviter la duplication.
EN: Centralize [INFO]/[WARN]/[DBG] messages and progress helpers.

No-behavior-change:
- Conserver exactement le format actuel de sortie console lors de la migration.
"""

def info(msg: str) -> None:
    print(f"[INFO] {msg}")

def warn(msg: str) -> None:
    print(f"[WARN] {msg}")

def dbg(msg: str) -> None:
    print(f"[DBG] {msg}")

def progress(prefix: str, i: int, total: int, label: str = "") -> None:
    if total <= 0:
        return
    pct = (i / total) * 100.0
    if label:
        print(f"{prefix}: {i}/{total} ({pct:5.1f}%) — {label}")
    else:
        print(f"{prefix}: {i}/{total} ({pct:5.1f}%)")
