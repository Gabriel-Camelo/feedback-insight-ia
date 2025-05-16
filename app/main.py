from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, get_db
from app import models
from app.routers import feedbacks, purchases, labels

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Feedback Analysis API",
    description="API for processing customer feedback with AI",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedbacks.router)
app.include_router(purchases.router)
app.include_router(labels.router)

@app.get("/")
def read_root():
    return {"message": "Feedback Analysis API is running"}