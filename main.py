from fastapi import FastAPI
from app.db import engine, Base
import app.models  # Ensure models are imported
from app.routes import router as user_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(user_router, prefix="/users", tags=["users"])

@app.get("/")
def root():
    return {"message": "SaaS Payment System Backend is running."} 