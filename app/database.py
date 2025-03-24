import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


#loading env varianles
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
 
Base = declarative_base()


if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set! Check .env file.")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("successfully connected")
except Exception as e:
    print("database connection -- Failed")
    print(e)


SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

#dependecy to get a session of database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

