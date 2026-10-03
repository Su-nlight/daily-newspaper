from fastapi import APIRouter, HTTPException

from app.models.edition import Edition
from app.services import sources

router = APIRouter(prefix="/api", tags=["edition"])


@router.get("/edition/today", response_model=Edition)
async def get_today_edition() -> Edition:
    return sources.get_today_edition()


@router.get("/edition/{date}", response_model=Edition)
async def get_edition_by_date(date: str) -> Edition:
    edition = sources.get_edition_by_date(date)
    if edition is None:
        raise HTTPException(status_code=404, detail="Edition not found")
    return edition
