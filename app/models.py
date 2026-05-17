from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, nullable=False)
    role = Column(String, nullable=False)
    link = Column(String, nullable=True)
    app_type = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    stage = Column(String, default="applied")
    applied_date = Column(Date, nullable=False)
    response_date = Column(Date, nullable=True)
    notes = Column(String, nullable=True)
