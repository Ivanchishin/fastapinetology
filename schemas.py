from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AdvertisementBase(BaseModel):
    title: str
    description: str
    price: float = Field(gt=0)
    author: str

class AdvertisementCreate(AdvertisementBase):
    pass

class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[str] = None

class AdvertisementResponse(AdvertisementBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True