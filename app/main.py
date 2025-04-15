from fastapi import FastAPI, Depends ,HTTPException, Request , Response  #  requests of ip tracking
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud,models,database #using databse.get_redis for redis
from pydantic import BaseModel,Field
import random
import string
from typing import Optional , List
import traceback
from datetime import datetime, timedelta, timezone
import httpx 
import asyncio 
import time
import os

# #slowapi imports 
# from slowapi import Limiter , _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
#ip tracking import 
#from starlette.requests import Request


# Intialize of fastapi
app = FastAPI(title="URL Shortener API")

#Schema of request
class ShortenRequest(BaseModel):
    long_url: str
    short_url: Optional[str] = None
    expiry_days: Optional[int] = 30
    
    
# schema of env update 
class ModeRequest(BaseModel):
    mode: str


#slowapi setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


# CORS 
origins = ["https://forgelink.netlify.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# database dependency 
async def get_db():
    async with database.SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
        

@app.get("/")
async def read_root():
    return {"message": "URL Shortener API is running!"}


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


@app.get("/healthz")
async def health_chk():
    return {"status":"ok"}



@app.post("/shorten/")
#@limiter.limit("10/minute")
async def shorten_url(request:Request , payload: ShortenRequest,db:AsyncSession = Depends(get_db)):
    if payload.expiry_days not in [5,15,30]:
        payload.expiry_days = 30 # default period
    
    max_attempts = 5
    attempt = 0 
    
    short_url = payload.short_url

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
    
    expires_at = datetime.now(timezone.utc) + timedelta(days= payload.expiry_days)

    new_url = await crud.create_url(
                                    db=db,
                                    long_url=payload.long_url,
                                    short_url=short_url,
                                    expires_at=expires_at
                                    )
    
    return {"id":new_url.id ,
            "long_url":new_url.long_url,
            "short_url":new_url.short_url,
            "expires_at":new_url.expires_at
              }

# redirect to long url
@app.get("/{short_url}")
async def get_url(short_url:str,request:Request,db:AsyncSession = Depends(get_db)):
    url_entry = await crud.get_url_by_short(db,short_url)
    if url_entry is None:
        raise HTTPException(status_code=404,detail="SHORT URL not FOUND")
    # logging analytics into redis
    try:
        redis = await database.get_redis()
        redis.rpush(f"analytics:{short_url}",
                        str({
                            "ip": request.client.host,
                            "timestamp":datetime.now(timezone.utc).isoformat()}))
    except Exception as e:
        print("reddis loggin failed: ",e)


    return RedirectResponse(url=url_entry.long_url) #redirection




#delete 
@app.delete("/{short_url}")
async def delete_url(short_url:str , db:AsyncSession = Depends(get_db)):
    deleted = await  crud.delete_url(db,short_url)
    if not deleted:
        raise HTTPException(status_code=404,detail="SHORT URL NOT FOUND")
    return {"message":"Short URL deleted successfully"}

#search
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
    


@app.get("/redirect/{short_url}")
async def redirect_with_protection(
    short_url : str,
    request : Request,
    db: AsyncSession = Depends(get_db)
):
    protection_modes = request.query_params.get("protection","").split(",")
    redis = await database.get_redis()
    client_ip = request.client.host

    if "rate_limit" in protection_modes:
        identifier = get_remote_address(request)
        try:
            limiter.check(request,"20/second",identifier)
        except RateLimitExceeded:
            raise HTTPException(status_code=429,detail="Rate limit exceeded")
    if "ip-block" in protection_modes:
        key = f"ddos:{client_ip}:{short_url}"
        count = await redis.incr(key)
        await redis.expire(key,60)
        if count > 50:
            raise HTTPException(status_code=403,detail="ip blocked ")
        

        
    
    
    if "captcha" in protection_modes:
        token = request.headers.get("x-Captcha-Token")
        if token != "valid":
            raise HTTPException(status_code=403,detail="Captcha validation failed")
    url = await crud.get_url_by_short(db,short_url)
    if not url:
        raise HTTPException(status_code=404,detail="SHORT URL not found")
    if url.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Short URL has expired")
    if "none" in protection_modes:
        return {"message": "No protection applied", "long_url": url.long_url}

    redis.rpush(f"analytics:{short_url}",str({
        "ip":client_ip,
        "timestamp":datetime.now(timezone.utc).isoformat()
    })) 
    return RedirectResponse(url=url.long_url)
    
#DDoS ATTACK SIMULATION FEATURE
@app.post("/simulate-ddos/{short_url}")
async def simulate_ddos(short_url: str, count: int = 100 , protection: str = "none", request: Request=None):
    if count>1000:
        raise HTTPException(status_code=400, detail="max 1000 requests  allowed")

    protection_modes = protection.split(",")
    print(f"[DDoS Simulation] Protection Mode: {protection}")

    start_time = time.time()
    success =0
    failed =0

    client_ip = request.client.host

    async def send_request(client,short_url):
        nonlocal success, failed
        try:
            headers ={}
            if "captcha" in protection_modes:
                headers["x-Captcha-Token"] = "valid" #dummy token

            url = f"http://localhost:8000/redirect/{short_url}?protection={protection}"
            response = await client.get(url,headers=headers)
            print(f"Request -> {response.status_code}")
            if response.status_code in [200,307]:
                success+=1
            else:
                failed+=1
        except Exception as e:
            failed +=1
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        tasks = [send_request(client,short_url) for _ in range(count) ]
        await asyncio.gather(*tasks)

    elapsed = round(time.time() - start_time,2)  

    return {
        "message": f"simulated  {count} requests to /redi/{short_url}",
        "success": success,
        "failed" : failed,
        "time_taken_sec": elapsed,
        "protection_mode" : protection
    }




@app.get("/analytics/{short_url}")
async def get_analytics(short_url:str):
    redis = await database.get_redis()
    try:
        logs = await redis.lrange(f"analytics:{short_url}",0,-1)
        protection_summary ={}
        # total_request = len(logs)

        # blocked_request =0
        # success_request =0
        # last_accessed = None
        # protection_mode = None
        
        for entry in logs:
            try:
                data = eval(entry)
                raw_mode = data.get("protection_mode", "none")
                modes = [m.strip().replace("-", "_") for m in raw_mode.split(",") if m.strip()]
                if not modes:
                    modes = ["none"]

                status = data.get("status","success")
                timestamp = data.get("timestamp")




                for mode in modes:
                    if mode not in protection_summary:
                        protection_summary[mode] ={
                            "total": 0,
                            "success": 0,
                            "blocked": 0,
                            "last_accessed": data.get("timestamp", None)

                        }
                    
                    protection_summary[mode]["total"]+=1
                    
                    if status == "blocked":
                        protection_summary[mode]["blocked"] +=1
                    else:
                        protection_summary[mode]["success"] +=1
                    
                    # last_accessed = data.get("timestamp",last_accessed)
                    # protection_mode =  data.get("protection_mode",protection_mode)
                    if timestamp > protection_summary[mode]["last_accessed"]:
                        protection_summary[mode]["last_accessed"] = timestamp

            except Exception as e:
                print("analytics parsing error: ",e)
        return {
            "short_url": short_url,
            "analytics": protection_summary
            # "total_request": total_request,
            # "success_request": success_request,
            # "blocked_request": blocked_request,
            # "last_accessed": last_accessed,
            # "protection_mode": protection_mode or "none"

        }

    except Exception as e:
        print("redis analytics error: ",e )
        raise HTTPException(status_code=500,detail="Failed to fetch Analytics")


@app.post("/reset-protection/{short_url}")
async def reset_protection(short_url: str, request: Request):
    redis = await database.get_redis()
    client_ip = request.client.host
    try:
        await redis.delete(f"ddos:{client_ip}:{short_url}")
        await redis.delete(f"analytics:{short_url}")
        return {"message":f"protection and analytics reset for {short_url}"}
    except Exception as e:
        print("reset protection failed: ",e )
        raise HTTPException(status_code=500,detail="reset failed")
    

@app.post("/set-mode")
async def set_mode(data: ModeRequest):
    mode = data.mode
    try:
        # Open the .env file in read-write mode
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        env_path = os.path.abspath(env_path)  # absolute path 
        print(f"Trying to open .env at: {env_path}")


        with open(env_path, "r+") as f:
            lines = f.readlines()
            f.seek(0)
            updated = False

            # Loop through lines and update LOCUST_PROTECTION_MODE if found
            for line in lines:
                if line.startswith("LOCUST_PROTECTION_MODE="):
                    f.write(f"LOCUST_PROTECTION_MODE={mode}\n")
                    updated = True
                else:
                    f.write(line)
            
            # If LOCUST_PROTECTION_MODE was not found, append it
            if not updated:
                f.write(f"LOCUST_PROTECTION_MODE={mode}\n")

            f.truncate()  # Ensure file is truncated to the correct size after writing

        return {"message": "Mode updated successfully", "mode": mode}

    except Exception as e:
        print("Error occurred while updating .env file:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to update mode: {str(e)}")

