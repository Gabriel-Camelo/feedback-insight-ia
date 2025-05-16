from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PurchaseBase(BaseModel):
    customer_id: str
    product_id: str
    product_name: str
    amount: float

class PurchaseCreate(PurchaseBase):
    pass

class Purchase(PurchaseBase):
    id: int
    purchase_date: datetime
    
    class Config:
        orm_mode = True

class LabelBase(BaseModel):
    name: str
    description: Optional[str] = None

class LabelCreate(LabelBase):
    pass

class Label(LabelBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True  # Novo no Pydantic v2

class FeedbackLabelBase(BaseModel):
    pass

class FeedbackLabel(FeedbackLabelBase):
    id: int
    label: Label  # Agora referenciamos o Label completo
    
    class Config:
        orm_mode = True
        from_attributes = True

class FeedbackBase(BaseModel):
    purchase_id: int
    comment: str

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    sentiment_score: float
    sentiment_label: str
    created_at: datetime
    labels: List[FeedbackLabel] = Field(default_factory=list)  # Usamos FeedbackLabel aqui
    
    class Config:
        orm_mode = True
        from_attributes = True