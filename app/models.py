from sqlalchemy import Column,Integer,String,Text , DateTime
from app.database import Base
from datetime import datetime , timezone


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer,primary_key=True)
    long_url = Column(Text,nullable=False)
    short_url = Column(String(10),unique=True,index=True,nullable=False)
    created_at = Column(DateTime(timezone=True), default= datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)