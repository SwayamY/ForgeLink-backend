import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from sqlalchemy.orm import declarative_base, sessionmaker


#loading env varianles
load_dotenv()
POSTGRES_USER = os.getenv("POSTGRES_USER",'sweyam')
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")  # Default to 'pgbouncer' if not set
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")  # Default to 6432


# DEBUG: Print to check if variables are loaded correctly
print(f"POSTGRES_USER={POSTGRES_USER}")
print(f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}")
print(f"POSTGRES_DB={POSTGRES_DB}")
print(f"POSTGRES_HOST={POSTGRES_HOST}")
print(f"POSTGRES_PORT={POSTGRES_PORT}")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
 




if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://","postgresql+asyncpg://",1)

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
if DEBUG:
    print(f"Using DATABASE_URL: {DATABASE_URL}")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set! Check .env file.")

Base = declarative_base()
print(f"Using DATABASE_URL: {DATABASE_URL}")  # Debugging line


engine: AsyncEngine = create_async_engine(DATABASE_URL,echo=DEBUG)


SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit= False
    )

async def get_db():
    async with SessionLocal() as db:
        yield db

async def test_connection():
    try:
        async with engine.begin() as conn:
            print("success connected to DB")
    except Exception as e:
        print("DB connection Failed")
        print(e)

if __name__ == "__main__":
    try:
        asyncio.run(test_connection())
    except RuntimeError:
        print("async event loop already running. Skipping test conn")