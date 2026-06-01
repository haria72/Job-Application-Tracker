from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from typing import List, Optional

router = APIRouter()

#add a new application
@router.post("/applications", response_model=ApplicationResponse)
def create_application(app: ApplicationCreate, db: Session = Depends(get_db)):
    new_app = models.Application(**app.model_dump()) #unpack the Pydantic model into a dictionary and pass it to the SQLAlchemy model constructor
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

@router.get("/applications", response_model=List[ApplicationResponse])
def get_applications(company: Optional[str] = None, stage: Optional[str] = None, platform: Optional[str] = None, app_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Application)
    if company:
        query = query.filter(models.Application.company.ilike(f"%{company}%")) #case-insensitive search for company name containing the given string
    if stage:
        query = query.filter(models.Application.stage == stage)
    if platform:
        query = query.filter(models.Application.platform == platform)
    if app_type:
        query = query.filter(models.Application.app_type == app_type)
    return query.all()

@router.patch("/applications/{app_id}", response_model=ApplicationResponse)
def update_application(app_id: int, updates: ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(app, key, value)
    db.commit()
    db.refresh(app)
    return app

@router.delete("/applications/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app)
    db.commit()
    return {"detail": "Application deleted successfully"}