from fastapi import FastAPI, Depends ,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud,models,database
from pydantic import BaseModel

app = FastAPI(title="URL Shortener API")


class ShortenRequest(BaseModel):
    long_url: str
    short_url: str

async def get_db():
    async with database.SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
        

@app.get("/")
async def read_root():
    return {"message": "URL Shortener API is running!"}

@app.post("/shorten/")
async def shorten_url(request:ShortenRequest,db:AsyncSession = Depends(get_db)):
    existing = await crud.get_url_by_short(db,request.short_url)
    if existing:
        raise HTTPException(status_code=400, detail="SHORT URL already exists")

    new_url = await crud.create_url(db,request.long_url,request.short_url)
    return {"id":new_url.id ,"long_url":new_url.long_url, "short_url":new_url.short_url}


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