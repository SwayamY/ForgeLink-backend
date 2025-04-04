from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import URL
from datetime import datetime, timezone

async def create_url(db:AsyncSession, long_url:str, short_url:str, expires_at=None) -> URL | dict:
    existing = await get_url_by_short(db,short_url)
    if existing:
        print(f"Short URL already  exists: {short_url}") # debugging
        return {"error": "Short URL already exists", "short_url": short_url} # would resove error 400
    

    print(f"creating short URL : {short_url} for {long_url}")
    new_url = URL(long_url = long_url , short_url = short_url, expires_at = expires_at)
    db.add(new_url)
    await db.commit()
    await db.refresh(new_url)
    return new_url

async def get_url_by_short(db:AsyncSession,short_url:str):
    now = datetime.now(timezone.utc)
    result = await db.execute(
                            select(URL).where
                              (and_
                                (URL.short_url == short_url,
                               or_
                                (URL.expires_at.is_(None),
                                 URL.expires_at > now))))
    url_entry = result.scalars().first()
    print(f"checks if short URL exists: {short_url} --> {url_entry}")
    return url_entry

async def get_url_by_long(db:AsyncSession,long_url:str):
    result = await db.execute(select(URL).filter(URL.long_url == long_url))
    url_entry = result.scalars().first()
    print(f"check if long url exists: {long_url} --> {url_entry}")
    return url_entry

async def delete_url(db:AsyncSession,short_url:str):
    url_entry = await get_url_by_short(db,short_url)
    if url_entry:
        print(f"deleting short Url: {short_url}")
        await db.delete(url_entry)
        await db.commit()
        return True
    print(f"short url not found : {short_url}")
    return False

async def search_short_urls(db:AsyncSession, long_url: str):
    now = datetime.now(timezone.utc)
    result = await db.execute(select(URL).where(
                                and_(
                                URL.long_url == long_url,
                                or_(URL.expires_at.is_(None),URL.expires_at > now))
                                ))
    return result.scalars().all()
    
