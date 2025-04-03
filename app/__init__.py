import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .database import Base, engine

# Lifespan event for handling startup tasks
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # Continue running the app

# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)
