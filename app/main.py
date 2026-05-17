from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import router
from app.analytics import analytics_router

models.Base.metadata.create_all(bind=engine) #creates tables in the database based on the models defined in app/models.py

app = FastAPI()
app.include_router(router)
app.include_router(analytics_router)

@app.get("/")

def root():
    return {"message": "Welcome to the Job Application Tracker API!"}