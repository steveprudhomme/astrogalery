"""Cache local simple (JSON).

FR: Utilisé pour éviter de refaire des appels réseau (Simbad, Open-Meteo, Nova...).
EN: Used to avoid re-fetching network resources (Simbad, Open-Meteo, Nova...).

v0.8.1:
- Fournit un utilitaire générique; l'intégration se fera sans changer le comportement.
"""

from __future__ import annotations
from pathlib import Path
import json
from typing import Any

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class JsonCache:
    def __init__(self, path: Path):
        self.path = path
        self.data = load_json(path)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def persist(self) -> None:
        save_json(self.path, self.data)
