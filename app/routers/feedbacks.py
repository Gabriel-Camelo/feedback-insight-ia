from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.ai_processing import FeedbackAnalyzer
import app.models as models
import app.schemas as schemas
from app.database import get_db

router = APIRouter(prefix="/feedbacks", tags=["feedbacks"])
analyzer = FeedbackAnalyzer()

@router.post("/", response_model=schemas.Feedback)
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    # Check if purchase exists
    db_purchase = db.query(models.Purchase).filter(models.Purchase.id == feedback.purchase_id).first()
    if not db_purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    # Analyze sentiment
    sentiment = analyzer.analyze_sentiment(feedback.comment)
    
    # Map sentiment to label
    if sentiment["label"] in ["positive", "pos"]:
        sentiment["label"] = "Positivo"
    elif sentiment["label"] in ["negative", "neg"]:
        sentiment["label"] = "Negativo"
    else:
        sentiment["label"] = "Neutro"
    
    # Create feedback
    db_feedback = models.Feedback(
        purchase_id=feedback.purchase_id,
        comment=feedback.comment,
        sentiment_score=sentiment["score"],
        sentiment_label=sentiment["label"]
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    # Get existing labels
    existing_labels = [label.name for label in db.query(models.Label).all()]
    
    # Generate and assign labels
    generated_labels = analyzer.generate_labels(feedback.comment, existing_labels)
    
    for label_name in generated_labels:
        # Check if label exists
        db_label = db.query(models.Label).filter(models.Label.name == label_name).first()
        
        # If not, create it
        if not db_label:
            db_label = models.Label(name=label_name, description=f"Automatically generated for: {feedback.comment[:50]}...")
            db.add(db_label)
            db.commit()
            db.refresh(db_label)
        
        # Link label to feedback
        db_feedback_label = models.FeedbackLabel(
            feedback_id=db_feedback.id,
            label_id=db_label.id
        )
        db.add(db_feedback_label)
    
    db.commit()
    return db_feedback

@router.get("/", response_model=List[schemas.Feedback])
def read_feedbacks(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    feedbacks = (
        db.query(models.Feedback)
        .options(
            joinedload(models.Feedback.labels)
            .joinedload(models.FeedbackLabel.label)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    return feedbacks