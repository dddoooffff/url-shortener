from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas.schema import UrlCreate
from database.database import asyncSessionLocal
from database.models import Url_Short
from pydantic import HttpUrl, ValidationError

import secrets
import urllib.parse

router = APIRouter(prefix="/short-url")
templates = Jinja2Templates(directory="templates")

async def get_db():
    async with asyncSessionLocal() as db:
        yield db

@router.get("/", response_model=dict, response_class=HTMLResponse)
async def show_form(request: Request, message: str = None, short_url: str = None, db: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": message,
            "short_url": short_url
        }
    )
    

@router.post("/submit", response_model=dict)
async def handle_form(urlInp: str = Form(...), db: AsyncSession = Depends(get_db)):
    try:
        while True:
            validate_url = HttpUrl(urlInp)

            short_code = secrets.token_urlsafe(5)[:5]
            existing = await db.execute(
                select(Url_Short).where(Url_Short.short_code == short_code)
            )
            if not existing.scalar_one_or_none():
                break
            
            
        db_url = Url_Short(
            short_code = short_code,
            original_url = str(validate_url),
            clicks = 0
        )

        encoded_message = urllib.parse.quote("Ссылка успешно создана")
        encoded_short_url = urllib.parse.quote(f"https://shorter.com/{short_code}")
        encoded_original = urllib.parse.quote(str(validate_url))

        db.add(db_url)
        await db.commit()
        await db.refresh(db_url)

        return RedirectResponse(url=f"/short-url/?message={encoded_message}&short_url={encoded_short_url}&original_url={encoded_original}", status_code=303)

    except ValidationError:
        encoded_error = urllib.parse.quote("Некорректный URL")
        return RedirectResponse(
            url=f"/short-url/?message={encoded_error}",
            status_code=303
        )
    
    except Exception as e:
        encoded_error = urllib.parse.quote(f"Ошибка сервера: {str(e)}")
        return RedirectResponse(
            url=f"/short-url/?message={encoded_error}",
            status_code=303
        )

@router.get("/{short_code}")
async def redirect(short_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Url_Short).where(Url_Short.short_code == short_code))
    url = result.scalar_one_or_none()
    
    if not url:
        raise HTTPException(status_code=404)
    
    url.clicks += 1
    await db.commit()
    
    return RedirectResponse(url=url.original_url)


@router.get("/stats", response_model=dict, response_class=HTMLResponse)
async def get_stats(short: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Url_Short).where(Url_Short.short_code == short))
    url = result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "stats.html",
        {
            "original": url.original_url,
            "short": short,
            "clicks": url.clicks
        }
    )
    
@router.post("/stats/submit", response_model=dict)
async def handle_stats(shortInp: str, db: AsyncSession = Depends(get_db)):
    
    return RedirectResponse(url=f"/short-url/stats/?short={shortInp}", status_code=303)