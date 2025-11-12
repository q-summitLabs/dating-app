from sqlalchemy import Column, Integer, String, ARRAY, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "yolk_staging"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    interests = Column(ARRAY(String))
    location = Column(String)
    pictures = Column(ARRAY(String))
    prompts = Column(JSON)
