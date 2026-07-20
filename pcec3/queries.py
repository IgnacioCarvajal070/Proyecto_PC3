"""Consultas para interactuar con la base de datos"""

from typing import Any
from sqlmodel import Session, select, func
from pcec3.models import Category, Book


def total_items(session: Session) -> int:
    """Obtiene el número total de libros en la base de datos.
    Args:
        session (Session): Sesión de base de datos SQLModel.
    Returns:
        int: Número total de libros en la base de datos.
    """
    statement = select(func.count(Book.id))
    result = session.exec(statement).one_or_none()
    return int(result or 0)


def items_by_category(session: Session) -> list[tuple[str, int]]:
    """Obtiene el número de libros por categoría en la base de datos.
    Args:
        session (Session): Sesión de base de datos SQLModel.
    Returns:
        list[tuple[str, int]]: Lista de tuplas con el nombre de la categoría
        y el número de libros en esa categoría.
    """
    statement = (
        select(Category.name, func.count(Book.id).label("book_count"))
        .join(Book, isouter=True)
        .group_by(Category.name)
        .order_by(func.count(Book.id).desc())
    )
    result = session.exec(statement).all()
    return [(name, book_count) for name, book_count in result]


def get_best_rated_books(session: Session, limit: int = 10) -> list[Book]:
    """Obtiene los libros mejor valorados en la base de datos.
    Args:
        session (Session): Sesión de base de datos SQLModel.
        limit (int): Número máximo de libros a obtener.
    Returns:
        list[Book]: Lista de libros mejor valorados.
    """
    statement = select(Book).order_by(Book.rating.desc()).limit(limit)
    result = session.exec(statement).all()
    return result


def books_stats(session: Session) -> dict[str, Any]:
    """Obtiene estadísticas de los libros en la base de datos.
    Args:
        session (Session): Sesión de base de datos SQLModel.
    Returns:
        dict[str, Any]: Diccionario con estadísticas globales y por categoría.
    """
    global_stats = select(
        func.avg(Book.price), func.min(Book.price), func.max(Book.price)
    )
    avg_price, min_price, max_price = session.exec(global_stats).first() or (
        0.0,
        0.0,
        0.0,
    )
    category_stats = (
        select(
            Category.name,
            func.avg(Book.price),
            func.min(Book.price),
            func.max(Book.price),
        )
        .join(Book)
        .group_by(Category.name)
    )
    category_stats_result = session.exec(category_stats).all()
    stats_by_category: dict[str, dict[str, float]] = {
        name: {
            "avg_price": round(float(avg_price or 0.0), 2),
            "min_price": round(float(min_price or 0.0), 2),
            "max_price": round(float(max_price or 0.0), 2),
        }
        for name, avg_price, min_price, max_price in category_stats_result
    }
    return {
        "global": {
            "avg_price": round(float(avg_price or 0.0), 2),
            "min_price": round(float(min_price or 0.0), 2),
            "max_price": round(float(max_price or 0.0), 2),
        },
        "by_category": stats_by_category,
    }
