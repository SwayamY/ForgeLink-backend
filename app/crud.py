from sqlalchemy.orm import Session
from app.models import URL

def create_url(db:Session, long_url:str,short_url:str):
    existing = get_url_by_short(db,short_url)
    if existing:
        print(f"Short URL already already exists: {short_url}") # debugging
        return None # would resove error 400
    



    print(f"creating short URL : {short_url} for {long_url}")
    new_url = URL(long_url = long_url , short_url = short_url)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url

def get_url_by_short(db:Session,short_url:str):

    url_entry = db.query(URL).filter(URL.short_url == short_url).first()
    print(f"checks if short URL exists: {short_url} --> {url_entry}")
    return url_entry

def get_url_by_long(db:Session,long_url:str):
    url_entry = db.query(URL).filter(URL.long_url == long_url).first()
    print(f"check if long url exists: {long_url} --> {url_entry}")
    return url_entry

def delete_url(db:Session,short_url:str):
    url_entry = db.query(URL).filter(URL.short_url == short_url).first()
    if url_entry:
        print(f"deleting short Url: {short_url}")
        db.delete(url_entry)
        db.commit()
        return True
    print(f"short url not found : {short_url}")
    return False
