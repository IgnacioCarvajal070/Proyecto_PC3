"""Seeder para la persistencia de los datos scrapeados"""

import logging
from typing import Any
from pydantic import ValidationError
from sqlmodel import Session, select
from pcec3.database import get_session, create_db_and_tables
from pcec3.models import Category, Book
from pcec3.scraper import scrape_books

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_or_create_category(session: Session, category_name: str) -> Category:
    """Obtiene o crea una categoría en la base de datos.
    Args:
        session (Session): Sesión de base de datos SQLModel.
        category_name (str): Nombre de la categoría a obtener o crear.
    Returns:
        Category: La categoría obtenida o creada.
    """
    statement = select(Category).where(Category.name == category_name)
    category = session.exec(statement).first()
    if not category:
        category = Category(name=category_name)
        session.add(category)
        session.commit()
        session.refresh(category)
    return category


def book_exists(session: Session, title: str, category_id: int) -> bool:
    """Verifica si un libro ya existe en la base de datos.
    Args:
        session (Session): Sesión de base de datos SQLModel.
        title (str): Título del libro a verificar.
        category_id (int): ID de la categoría a la que pertenece el libro.
    Returns:
        bool: True si el libro existe, False en caso contrario.
    """
    statement = select(Book).where(Book.title == title, Book.category_id == category_id)
    return session.exec(statement).first() is not None


def process_and_save_books(
    session: Session, books: list[dict[str, Any]]
) -> tuple[int, int]:
    """Procesa y guarda los libros scrapeados en la base de datos.
    Args:
        session (Session): Sesión de base de datos SQLModel.
        books (list[dict[str, Any]]): Lista de diccionarios con los
        campos de los libros.
    Returns:
        tuple[int, int]: Tupla con el número de libros guardados y
        el número de libros omitidos.
    """
    saved_count = 0
    skipped_count = 0

    for book_data in books:
        category_name = book_data.pop("category_name")
        try:
            category = get_or_create_category(session, category_name)
            book_data["category_id"] = category.id

            if not book_exists(session, book_data["title"], category.id):
                book = Book(
                    title=book_data["title"],
                    price=book_data["price"],
                    availability=book_data["availability"],
                    rating=book_data["rating"],
                    url=book_data.get("url"),
                    category_id=category.id,
                )
                session.add(book)
                session.commit()
                saved_count += 1
            else:
                skipped_count += 1
        except (ValidationError, ValueError, KeyError) as e:
            session.rollback()
            logger.warning(
                f"Error procesando '{book_data.get('title', 'Desconocido')}': {e}"
            )
            skipped_count += 1
    return saved_count, skipped_count


def seed_db(min_items: int = 50) -> None:
    """Scrapea y guarda los libros en la base de datos.
    Args:
        min_items (int): Número mínimo de libros a scrapear.
    """
    create_db_and_tables()
    logger.info(f"Scrapeando libros hasta alcanzar un mínimo de {min_items} libros.")
    books = scrape_books(min_items=min_items)
    with get_session() as session:
        saved_count, skipped_count = process_and_save_books(session, books)
    logger.info(f"{saved_count} libros guardados, {skipped_count} libros omitidos.")
