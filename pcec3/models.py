"""Modelos de datos SQLModel para el scraping de datos"""

from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel


class Category(SQLModel, table=True):
    """Modelo que agrupa los libros por su categoría.
    Attributes:
        id (int): Identificador único de la categoría.
        name (str): Nombre de la categoría.
        books (list[Book]): Lista de libros asociados a la categoría.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    books: list["Book"] = Relationship(back_populates="category")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Valida que el nombre de la categoría no esté vacío y no contenga
        solo espacios en blanco.
        Args:
            value (str): Nombre de la categoría a validar.
        Returns:
            str: Nombre de la categoría validado.
        Raises:
            ValueError: Si el nombre de la categoría está vacío o contiene
            solo espacios en blanco.
        """
        if not value.strip():
            raise ValueError("El nombre de la categoría no puede estar vacío")
        return value.strip()


class Book(SQLModel, table=True):
    """Modelo que representa un libro.
    Attributes:
        id (int): Identificador único del libro.
        title (str): Título del libro.
        price (float): Precio del libro.
        availability (bool): Disponibilidad del libro.
        rating (int): Calificación del libro (1 a 5).
        url (str): URL de la página del libro.
        category_id (int): Identificador de la categoría asociada al libro.
        category (Category): Relación con la categoría asociada al libro.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    price: float = Field(ge=0.0)
    availability: bool
    rating: int = Field(ge=1, le=5)
    url: Optional[str] = Field(default=None)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="books")

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Valida que el título del libro no esté vacío y
            no contenga solo espacios en blanco.
        Args:
            value (str): Título del libro a validar.
        Returns:
            str: Título del libro validado.
        Raises:
            ValueError: Si el título del libro está vacío
            o contiene solo espacios en blanco.
        """
        if not value.strip():
            raise ValueError("El título del libro no puede estar vacío.")
        return value.strip()

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: float) -> float:
        """Valida que el precio del libro sea mayor o igual a cero.
        Args:
            value (float): Precio del libro a validar.
        Returns:
            float: Precio del libro validado.
        Raises:
            ValueError: Si el precio del libro es menor a cero.
        """
        if value <= 0.0:
            raise ValueError("El precio del libro debe ser mayor a cero.")
        return value

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value: int) -> int:
        """Valida que la calificación del libro esté entre 1 y 5.
        Args:
            value (int): Calificación del libro a validar.
        Returns:
            int: Calificación del libro validada.
        Raises:
            ValueError: Si la calificación del libro no está entre 1 y 5.
        """
        if value < 1 or value > 5:
            raise ValueError("La calificación del libro debe estar entre 1 y 5.")
        return value
