from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mileon_saas.config import settings
from mileon_saas.db import get_session
from mileon_saas.models import CarListing
from mileon_saas.schemas import CarListingCreate, CarListingRead, ListingWithScores
from mileon_saas.services.decision_engine import evaluate_listing
from mileon_saas.services.ingestion import ingest_from_json

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("", response_model=list[ListingWithScores])
async def list_listings(
    company_id: int = settings.default_company_id,
    brand: Optional[str] = None,
    with_scores: bool = True,
    session: AsyncSession = Depends(get_session),
):
    query = select(CarListing).where(CarListing.company_id == company_id)
    if brand:
        query = query.where(CarListing.brand == brand)

    listings = (await session.scalars(query)).all()
    results = []
    for listing in listings:
        if with_scores:
            scores = await evaluate_listing(session, listing)
            results.append(ListingWithScores(listing=CarListingRead.model_validate(listing), scores=scores))
        else:
            results.append(ListingWithScores(
                listing=CarListingRead.model_validate(listing),
                scores=None,
            ))

    return results


@router.get("/{listing_id}", response_model=CarListingRead)
async def get_listing(listing_id: int, session: AsyncSession = Depends(get_session)):
    listing = await session.get(CarListing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.post("", response_model=CarListingRead)
async def create_listing(
    payload: CarListingCreate,
    session: AsyncSession = Depends(get_session),
):
    listing = CarListing(**payload.model_dump())
    session.add(listing)
    await session.commit()
    await session.refresh(listing)
    return listing


@router.post("/ingest")
async def ingest_listings(
    path: str = "cars_data.json",
    company_id: int = settings.default_company_id,
    session: AsyncSession = Depends(get_session),
):
    count = await ingest_from_json(session, path, company_id)
    return {"ingested": count}
