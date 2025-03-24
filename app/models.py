from sqlalchemy import Column,Integer,String,Text
from app.database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer,primary_key=True)
    long_url = Column(Text,nullable=False)
    short_url = Column(String(10),unique=True,nullable=False)