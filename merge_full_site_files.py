from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def entry_score(item: dict[str, Any]) -> int:
    return sum(1 for value in item.values() if value not in (None, "", [], {}))


def load_items(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    except Exception as exc:
        print(f"Warning: Could not read {path}: {exc}")
    return []


def is_empty_json(path: Path) -> bool:
    if path.stat().st_size == 0:
        return True
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = handle.read().strip()
        if raw in {"", "[]", "{}"}:
            return True
        parsed = json.loads(raw)
        return parsed in ([], {})
    except Exception:
        return False


def main() -> None:
    root = Path(__file__).resolve().parent
    files = sorted(root.glob("full_site_*.json"), key=lambda path: path.stat().st_mtime)

    merged_by_id: dict[Any, dict[str, Any]] = {}

    for path in files:
        items = load_items(path)
        for item in items:
            car_id = item.get("car_id")
            if car_id is None:
                continue
            if car_id in merged_by_id:
                current = merged_by_id[car_id]
                if entry_score(item) > entry_score(current):
                    merged_by_id[car_id] = item
            else:
                merged_by_id[car_id] = item

    merged_items = list(merged_by_id.values())
    out_path = root / "full_site_merged.json"
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(merged_items, handle, ensure_ascii=False, indent=2)

    for path in root.glob("*.json"):
        if path.name == out_path.name:
            continue
        if is_empty_json(path):
            path.unlink()
            print(f"Removed empty JSON: {path}")

    print(f"Merged {len(files)} files into {out_path} with {len(merged_items)} unique items.")


if __name__ == "__main__":
    main()
