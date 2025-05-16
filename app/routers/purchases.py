from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import app.models as models
import app.schemas as schemas
from app.database import get_db

router = APIRouter(prefix="/purchases", tags=["purchases"])

@router.post("/", response_model=schemas.Purchase)
def create_purchase(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    db_purchase = models.Purchase(**purchase.dict())
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase

@router.get("/", response_model=List[schemas.Purchase])
def read_purchases(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    purchases = db.query(models.Purchase).offset(skip).limit(limit).all()
    return purchases