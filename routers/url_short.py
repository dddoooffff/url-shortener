from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas.schema import UrlCreate
from database.database import asyncSessionLocal
from database.models import Url_Short

import secrets

router = APIRouter(prefix="/short-url")

async def get_db():
    async with asyncSessionLocal() as db:
        yield db

@router.post("/", response_model=dict)
async def create_url(url: UrlCreate, db: AsyncSession = Depends(get_db)):
    short_code = secrets.token_urlsafe(5)[:5]
    
    existing_url = await db.execute(select(Url_Short).where(Url_Short.short_code == short_code))
    if existing_url.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Short code collision, please try again")
    
    db_url = Url_Short(
        short_code = short_code,
        original_url = url.original_url,
        clicks = 0
    )
    
    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)
    
    return {"short_url": f"https://my-domen.com/{short_code}"}

@router.get("/{short_code}")
async def redirect(short_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Url_Short).where(Url_Short.short_code == short_code))
    url = result.scalar_one_or_none()
    
    if not url:
        raise HTTPException(status_code=404)
    
    url.clicks += 1
    await db.commit()
    
    return RedirectResponse(url=url.original_url)


@router.get("/stats/{short_code}", response_model=dict)
async def get_stats(short_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Url_Short).where(Url_Short.short_code == short_code))
    url = result.scalar_one_or_none()
    
    if not url:
        raise HTTPException(status_code=404)
    
    return {
        "original_url": url.original_url,
        "short_code": url.short_code,
        "clicks": url.clicks
    }