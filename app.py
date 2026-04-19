from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Создание объявления
@app.post("/advertisement", response_model=schemas.AdvertisementResponse)
def create_advertisement(ad: schemas.AdvertisementCreate, db: Session = Depends(get_db)):
    db_ad = models.Advertisement(**ad.dict())
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


# Получение объявления по ID
@app.get("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def get_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    ad = db.query(models.Advertisement).get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


# Обновление объявления
@app.patch("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def update_advertisement(
        advertisement_id: int,
        ad_update: schemas.AdvertisementUpdate,
        db: Session = Depends(get_db)
):
    ad = db.query(models.Advertisement).get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    for key, value in ad_update.dict(exclude_unset=True).items():
        setattr(ad, key, value)

    db.commit()
    db.refresh(ad)
    return ad


# Удаление объявления
@app.delete("/advertisement/{advertisement_id}")
def delete_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    ad = db.query(models.Advertisement).get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    db.delete(ad)
    db.commit()
    return {"status": "deleted"}


# Получить список всех объявлений
@app.get("/advertisement", response_model=List[schemas.AdvertisementResponse])
def search_advertisements(
        title: Optional[str] = Query(None),
        author: Optional[str] = Query(None),
        min_price: Optional[float] = Query(None),
        max_price: Optional[float] = Query(None),
        db: Session = Depends(get_db)
):
    query = db.query(models.Advertisement)

    if title:
        query = query.filter(models.Advertisement.title.contains(title))
    if author:
        query = query.filter(models.Advertisement.author.contains(author))
    if min_price is not None:
        query = query.filter(models.Advertisement.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Advertisement.price <= max_price)

    return query.all()