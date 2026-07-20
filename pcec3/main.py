"""Main del proyecto EC3"""

from sqlmodel import Session
from tabulate import tabulate
from pcec3.database import get_session
from pcec3.queries import (
    books_stats,
    get_best_rated_books,
    items_by_category,
    total_items,
)
from pcec3.seed import seed_db


def display_total_items(session: Session) -> None:
    """Muestra en terminal el número total de libros almacenados.
    Args:
        session: Sesión activa de base de datos SQLModel.
    """
    total = total_items(session)
    print("\n--- CONSULTA 1: VERIFICACIÓN BÁSICA ---")
    print(f"Total de libros registrados en BD: {total}")


def display_items_by_category(session: Session) -> None:
    """Muestra una tabla simple con los libros agrupados por categoría.
    Args:
        session: Sesión activa de base de datos SQLModel.
    """
    results = items_by_category(session)
    print("\n--- CONSULTA 2: ÍTEMS POR CATEGORÍA (TOP 10) ---")
    top_results = results[:10]
    headers = ["Categoría", "Cantidad de Libros"]
    print(tabulate(top_results, headers=headers, tablefmt="simple"))


def display_best_rated_books(session: Session) -> None:
    """Muestra una tabla simple con los libros mejor valorados.
    Args:
        session: Sesión activa de base de datos SQLModel.
    """
    books = get_best_rated_books(session, limit=10)
    print("\n--- CONSULTA 3: TOP 10 LIBROS MEJOR VALORADOS ---")
    table_data = []
    for book in books:
        title_short = book.title[:40] + "..." if len(book.title) > 40 else book.title
        table_data.append(
            [book.id, title_short, f"£{book.price:.2f}", f"{book.rating}/5"]
        )
    headers = ["ID", "Título", "Precio", "Valoración"]
    print(tabulate(table_data, headers=headers, tablefmt="simple"))


def display_books_stats(session: Session) -> None:
    """Muestra un resumen de estadísticas globales y por categoría.
    Args:
        session: Sesión activa de base de datos SQLModel.
    """
    stats = books_stats(session)
    global_s = stats["global"]
    cat_s = stats["by_category"]
    print("\n--- CONSULTA 4: ESTADÍSTICAS DESCRIPTIVAS DE PRECIO ---")
    print("\n[Estadísticas Globales]")
    table_global = [
        ["Precio Promedio", f"£{global_s['avg_price']:.2f}"],
        ["Precio Mínimo", f"£{global_s['min_price']:.2f}"],
        ["Precio Máximo", f"£{global_s['max_price']:.2f}"],
    ]
    print(tabulate(table_global, headers=["Métrica", "Valor"], tablefmt="simple"))
    print("\n[Estadísticas por Categoría - Top 10]")
    table_cat = []
    for name, m in list(cat_s.items())[:10]:
        table_cat.append(
            [
                name,
                f"£{m['avg_price']:.2f}",
                f"£{m['min_price']:.2f}",
                f"£{m['max_price']:.2f}",
            ]
        )
    headers_cat = ["Categoría", "Promedio", "Mínimo", "Máximo"]
    print(tabulate(table_cat, headers=headers_cat, tablefmt="simple"))


def main() -> None:
    """Ejecuta el pipeline de scraping, persistencia y consultas en SQLite."""
    print("=====================================================")
    print(" INICIANDO PIPELINE DE SCRAPING EC3")
    print("=====================================================")
    seed_db(min_items=50)
    print("\n=====================================================")
    print(" RESULTADOS DE LAS CONSULTAS EN SQLITE")
    print("=====================================================")
    with get_session() as session:
        display_total_items(session)
        display_items_by_category(session)
        display_best_rated_books(session)
        display_books_stats(session)
    print("\n=====================================================")
    print(" PROCESO FINALIZADO CON ÉXITO")
    print("=====================================================")


if __name__ == "__main__":
    main()
