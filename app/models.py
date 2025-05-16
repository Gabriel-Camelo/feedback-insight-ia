from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Purchase(Base):
    __tablename__ = "purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    product_id = Column(String, index=True)
    product_name = Column(String)
    amount = Column(Float)
    purchase_date = Column(DateTime(timezone=True), server_default=func.now())
    
    feedbacks = relationship("Feedback", back_populates="purchase")

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    comment = Column(Text)
    sentiment_score = Column(Float)
    sentiment_label = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    purchase = relationship("Purchase", back_populates="feedbacks")
    labels = relationship("FeedbackLabel", back_populates="feedback")

class Label(Base):
    __tablename__ = "labels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    feedbacks = relationship("FeedbackLabel", back_populates="label")

class FeedbackLabel(Base):
    __tablename__ = "feedback_labels"
    
    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id"))
    label_id = Column(Integer, ForeignKey("labels.id"))
    
    feedback = relationship("Feedback", back_populates="labels")
    label = relationship("Label", back_populates="feedbacks")