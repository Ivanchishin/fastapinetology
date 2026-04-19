from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    author = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)