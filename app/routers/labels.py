from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import app.models as models
import app.schemas as schemas
from app.database import get_db

router = APIRouter(prefix="/labels", tags=["labels"])

@router.post("/", response_model=schemas.Label)
def create_purchase(label: schemas.LabelCreate, db: Session = Depends(get_db)):
    db_label = models.Label(**label.dict())
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label

@router.get("/", response_model=List[schemas.Label])
def read_labels(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    labels = db.query(models.Label).offset(skip).limit(limit).all()
    return labels