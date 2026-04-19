from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from typing import Optional

from database import SessionLocal
from models import Advertisement
from schemas import (
    AdvertisementCreate,
    AdvertisementUpdate,
    AdvertisementResponse,
    AdvertisementListResponse,
)

router = APIRouter(prefix="/advertisement", tags=["advertisement"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=AdvertisementResponse, status_code=201)
def create_advertisement(ad: AdvertisementCreate, db: Session = Depends(get_db)):
    db_ad = Advertisement(**ad.model_dump())
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


@router.get("/{advertisement_id}", response_model=AdvertisementResponse)
def get_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    ad = db.get(Advertisement, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@router.patch("/{advertisement_id}", response_model=AdvertisementResponse)
def update_advertisement(
        advertisement_id: int,
        ad_update: AdvertisementUpdate,
        db: Session = Depends(get_db),
):
    ad = db.get(Advertisement, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    for key, value in ad_update.model_dump(exclude_unset=True).items():
        setattr(ad, key, value)

    db.commit()
    db.refresh(ad)
    return ad



@router.delete("/{advertisement_id}")
def delete_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    ad = db.get(Advertisement, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    db.delete(ad)
    db.commit()
    return {"status": "deleted"}


@router.get("", response_model=AdvertisementListResponse)
def search_advertisements(
        title: Optional[str] = Query(None),
        author: Optional[str] = Query(None),
        min_price: Optional[float] = Query(None, gt=0),
        max_price: Optional[float] = Query(None, gt=0),
        limit: int = Query(10, ge=1),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
):
    query = db.query(Advertisement)

    if title and author:
        query = query.filter(
            or_(
                Advertisement.title.ilike(f"%{title}%"),
                Advertisement.author.ilike(f"%{author}%"),
            )
        )
    else:
        if title:
            query = query.filter(Advertisement.title.ilike(f"%{title}%"))
        if author:
            query = query.filter(Advertisement.author.ilike(f"%{author}%"))

    # фильтр по цене
    if min_price is not None:
        query = query.filter(Advertisement.price >= min_price)
    if max_price is not None:
        query = query.filter(Advertisement.price <= max_price)

    total = query.count()

    items = query.offset(offset).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }