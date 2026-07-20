"""Módulo para gestionar la conexión a la base de datos SQLModel."""

from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

DB_PATH = Path("data.db").resolve()
DB_URL = f"sqlite:///{DB_PATH}"

engine: Engine = create_engine(
    DB_URL, echo=False, connect_args={"check_same_thread": False}
)


def create_db_and_tables() -> None:
    """Crea la base de datos y las tablas definidas en los modelos SQLModel."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Crea y devuelve una sesión de base de datos SQLModel.
    Returns:
        Session: Una sesión de base de datos SQLModel.
    """
    return Session(engine)
