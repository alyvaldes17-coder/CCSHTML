from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional

DATABASE_URL = "sqlite:///./nike_bot.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

def create_db_and_tables():
    """Crear tablas en DB"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency para sesión de BD"""
    with Session(engine) as session:
        yield session
