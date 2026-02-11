import json
from pathlib import Path
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mileon_saas.config import settings
from mileon_saas.models import CarListing


def _load_json(path: str) -> list[dict]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _map_record(record: dict, company_id: int) -> dict:
    return {
        "company_id": company_id,
        "source": "myauto",
        "source_listing_id": str(record.get("car_id")) if record.get("car_id") else None,
        "brand": record.get("make_name") or "unknown",
        "model": record.get("model") or "unknown",
        "year": record.get("year"),
        "engine_type": None,
        "engine_code": None,
        "engine_volume": record.get("engine_volume"),
        "transmission": None,
        "transmission_code": None,
        "drivetrain": None,
        "mileage_km": record.get("mileage_km"),
        "price_usd": record.get("price_usd"),
        "owners_count": record.get("owners_count"),
        "accident_history": record.get("accident_history"),
        "imported_from": record.get("imported_from"),
        "vin": record.get("vin"),
    }


async def ingest_from_json(session: AsyncSession, path: str, company_id: int | None = None) -> int:
    company_id = company_id or settings.default_company_id
    payload = _load_json(path)
    if not payload:
        return 0

    new_count = 0
    for record in payload:
        mapped = _map_record(record, company_id)
        source_id = mapped.get("source_listing_id")
        if source_id:
            existing = await session.scalar(
                select(CarListing).where(
                    CarListing.company_id == company_id,
                    CarListing.source == "myauto",
                    CarListing.source_listing_id == source_id,
                )
            )
            if existing:
                continue

        session.add(CarListing(**mapped))
        new_count += 1

    await session.commit()
    return new_count
