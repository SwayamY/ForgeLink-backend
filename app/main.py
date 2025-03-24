from fastapi import FastAPI, Depends ,HTTPException
from sqlalchemy.orm import Session
from app import crud,models,database
from pydantic import BaseModel

app = FastAPI(title="URL Shortener API")


class ShortenRequest(BaseModel):
    long_url: str
    short_url: str

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


#would have used async but not good for small api but good whe dealing woth tousands of requests 
@app.post("/shorten/")
def shorten_url(request:ShortenRequest,db:Session = Depends(get_db)):
    existing = crud.get_url_by_short(db,request.short_url)
    if existing:
        raise HTTPException(status_code=400, detail="SHORT URL already exists")

    new_url =crud.create_url(db,request.long_url,request.short_url)
    return {"id":new_url.id ,"long_url":new_url.long_url, "short_url":new_url.short_url}


@app.get("/{short_url}")
def get_url(short_url:str,db:Session = Depends(get_db)):
    url_entry = crud.get_url_by_short(db,short_url)
    if url_entry is None:
        raise HTTPException(status_code=404,detail="SHORT URL not FOUND")
    return {"long_url":url_entry.long_url}

@app.delete("/{short_url}")
def delete_url(short_url:str , db:Session = Depends(get_db)):
    deleted = crud.delete_url(db,short_url)
    if not deleted:
        raise HTTPException(status_code=404,detail="SHORT URL NOT FOUND")
    return {"message":"Short URL deleted successfully"}