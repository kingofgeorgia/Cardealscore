from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Mapping of car manufacturer IDs to names (from mileon_saas/services/full_site_parser.py)
MAKE_NAMES = {
    1: "Alfa Romeo",
    2: "Audi",
    3: "BMW",
    5: "Chevrolet",
    7: "Ford",
    10: "Dodge",
    11: "GMC",
    12: "Honda",
    14: "Hyundai",
    16: "Infiniti",
    18: "Jaguar",
    19: "Jeep",
    20: "Kia",
    22: "Land Rover",
    23: "Lexus",
    24: "Mazda",
    25: "Mercedes-AMG",
    28: "MINI",
    29: "Mitsubishi",
    30: "Nissan",
    31: "Opel",
    33: "Porsche",
    34: "Renault",
    38: "Skoda",
    39: "Subaru",
    41: "Toyota",
    42: "Volkswagen",
    43: "Volvo",
    53: "Chrysler",
    61: "Smart",
    75: "Maserati",
    89: "BYD",
    110: "Hummer",
    124: "Polestar",
    155: "Tesla",
    161: "Zeekr",
    394: "Bentley",
    786: "Alfa Romeo",
    987: "Can-Am",
}


def normalize_model(name: str) -> str:
    return " ".join(name.split()).strip()


def load_items(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    except Exception:
        return []
    return []


def main() -> None:
    root = Path(__file__).resolve().parent
    files = sorted(root.glob("full_site_*.json"))

    # man_id -> {make_name: str, models: {model_id: set(names)}, fallback_models: set(names)}
    result: dict[int, dict[str, Any]] = {}

    for path in files:
        items = load_items(path)
        if not items:
            continue
        for item in items:
            man_id = item.get("make") if isinstance(item.get("make"), int) else item.get("man_id")
            model_id = item.get("model_id")
            model = item.get("model") if isinstance(item.get("model"), str) else item.get("car_model")

            if not isinstance(man_id, int):
                continue

            model_clean = normalize_model(model) if isinstance(model, str) else ""
            make_name = item.get("make_name") or MAKE_NAMES.get(man_id, f"Unknown ({man_id})")

            entry = result.setdefault(
                man_id,
                {"make_name": make_name, "models": {}, "fallback_models": set()},
            )

            if isinstance(model_id, int):
                entry["models"].setdefault(model_id, set())
                if model_clean:
                    entry["models"][model_id].add(model_clean)
            elif model_clean:
                entry["fallback_models"].add(model_clean)

    output: dict[str, dict[str, Any]] = {}
    for man_id, entry in sorted(result.items(), key=lambda item: item[0]):
        models: list[dict[str, Any]] = []
        for model_id, names in sorted(entry["models"].items(), key=lambda item: item[0]):
            name = sorted(names, key=lambda value: value.casefold())[0] if names else ""
            models.append({"model_id": model_id, "model": name})

        fallback_models = sorted(entry["fallback_models"], key=lambda value: value.casefold())
        output[str(man_id)] = {
            "make_name": entry["make_name"],
            "models": models,
            "fallback_models": fallback_models,
        }

    out_path = root / "mansNModels.json"
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=True, indent=2)

    print(f"Wrote {out_path} with {len(output)} makes from {len(files)} files.")


if __name__ == "__main__":
    main()
