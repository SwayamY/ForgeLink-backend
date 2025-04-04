from fastapi import FastAPI, Depends ,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud,models,database
from pydantic import BaseModel,Field
import random
import string
from typing import Optional , List
import traceback
from datetime import datetime, timedelta, timezone


app = FastAPI(title="URL Shortener API")


class ShortenRequest(BaseModel):
    long_url: str
    short_url: Optional[str] = None
    expiry_days: Optional[int] = 30

async def get_db():
    async with database.SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
        

@app.get("/")
async def read_root():
    return {"message": "URL Shortener API is running!"}

@app.get("/healthz")
async def health_chk():
    return {"status":"ok"}



@app.post("/shorten/")
async def shorten_url(request:ShortenRequest,db:AsyncSession = Depends(get_db)):
    if request.expiry_days not in [5,15,30]:
        request.expiry_days = 30 # default period
    
    max_attempts = 5
    attempt = 0 
    
    short_url = request.short_url

    if not short_url:
        while attempt < max_attempts:
            short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            existing = await crud.get_url_by_short(db,short_url)
            if not existing:
                break
            attempt +=1
            print(f"collison attempt {attempt}:'{short_url}' already exists")

        if attempt == max_attempts:
            raise HTTPException(status_code=500,detail="Failed to generate unique short url")
    else:
        existing = await crud.get_url_by_short(db,short_url)
        if existing:
            raise HTTPException(status_code=400, detail="SHORT URL already exists")
    
    expires_at = datetime.now(timezone.utc) + timedelta(days= request.expiry_days)

    new_url = await crud.create_url(
                                    db=db,
                                    long_url=request.long_url,
                                    short_url=short_url,
                                    expires_at=expires_at
                                    )
    
    return {"id":new_url.id ,
            "long_url":new_url.long_url,
            "short_url":new_url.short_url,
            "expires_at":new_url.expires_at
              }


@app.get("/{short_url}")
async def get_url(short_url:str,db:AsyncSession = Depends(get_db)):
    url_entry = await crud.get_url_by_short(db,short_url)
    if url_entry is None:
        raise HTTPException(status_code=404,detail="SHORT URL not FOUND")
    return RedirectResponse(url=url_entry.long_url)

@app.delete("/{short_url}")
async def delete_url(short_url:str , db:AsyncSession = Depends(get_db)):
    deleted = await  crud.delete_url(db,short_url)
    if not deleted:
        raise HTTPException(status_code=404,detail="SHORT URL NOT FOUND")
    return {"message":"Short URL deleted successfully"}

@app.get("/search/")
async def search_url(long_url:str ,db: AsyncSession = Depends(get_db)):
    try:
        print(f"[DEBUG] Searching short URLs for: {long_url}")  # Debug line
        urls = await crud.search_short_urls(db, long_url)
        if not urls:
            return {
                "message":"",
                "suggested_action": {
                   "method": "POST",
                   "url" :"/shorten/",
                   "body" : {
                       
                   "long_url": long_url
                   }
                }
            }

        return [{"short_url": url.short_url,"expires_at": url.expires_at} for url in urls]
    except Exception as e:
        print("error => ",e)
        traceback.print_exc()
        raise HTTPException(status_code=500,detail="Somewthing went wrong")