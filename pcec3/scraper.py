"""Módulo para el web scraping de libros"""

import logging
from typing import Any
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "http://books.toscrape.com/"

RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def get_driver() -> webdriver.Chrome:
    """Crea y devuelve un controlador de Selenium para Chrome en modo headless.
    Returns:
        webdriver.Chrome: Un controlador de Selenium para Chrome.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    return driver


def parse_book_element(
    book_element: WebElement, category_name: str
) -> dict[str, Any] | None:
    """Extrae los campos de un libro a partir de un elemento WebElement.
    Args:
        book_element (WebElement): Elemento WebElement que
        representa un libro.
        category_name (str): Nombre de la categoría a la
        que pertenece el libro.
    Returns:
        dict[str, Any] | None: Diccionario con los campos del libro
        o None si ocurre un error.
    """
    try:
        link_element = book_element.find_element(By.CSS_SELECTOR, "h3 > a")
        title = link_element.get_attribute("title")
        url = link_element.get_attribute("href")
        price_text = book_element.find_element(By.CSS_SELECTOR, ".price_color").text
        price = float(price_text.replace("£", "").strip())
        rating_element = book_element.find_element(By.CSS_SELECTOR, ".star-rating")
        rating_class = rating_element.get_attribute("class") or ""
        rating = 0
        for class_name, value in RATINGS.items():
            if class_name in rating_class.split():
                rating = value
                break
        availability_text = book_element.find_element(
            By.CSS_SELECTOR, ".instock.availability"
        ).text
        availability = "In stock" in availability_text
        return {
            "title": title,
            "url": url,
            "price": price,
            "rating": rating,
            "availability": availability,
            "category_name": category_name,
        }

    except (NoSuchElementException, ValueError, AttributeError) as e:
        logger.error(f"Error al parsear el elemento del libro: {e}")
        return None


def scrape_books_from_category(
    driver: webdriver.Chrome, wait: WebDriverWait, category_name: str
) -> list[dict[str, Any]]:
    """Scrapea los libros de una categoría específica.
    Args:
        driver (webdriver.Chrome): Controlador de Selenium para Chrome.
        wait (WebDriverWait): Objeto WebDriverWait para esperar elementos.
        category_name (str): Nombre de la categoría a scrapear.
    Returns:
        list[dict[str, Any]]: Lista de diccionarios
        con los campos de los libros.
    """
    category_books: list[dict[str, Any]] = []

    while True:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.product_pod"))
        )
        book_elements = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")
        for book_element in book_elements:
            book_data = parse_book_element(book_element, category_name)
            if book_data:
                category_books.append(book_data)
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.next > a")
            url_next = next_button.get_attribute("href")
            if url_next:
                driver.get(url_next)
            else:
                break
        except NoSuchElementException:
            break
    return category_books


def scrape_books(min_items: int = 50) -> list[dict[str, Any]]:
    """Scrapea los libros de todas las categorías
        hasta alcanzar un mínimo de libros.
    Args:
        min_items (int): Número mínimo de libros a scrapear.
    Returns:
        list[dict[str, Any]]: Lista de diccionarios
        con los campos de los libros.
    """
    driver = get_driver()
    wait = WebDriverWait(driver, 10)
    all_books: list[dict[str, Any]] = []

    try:
        driver.get(BASE_URL)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".side_categories ul li ul li a")
            )
        )
        category_elements = driver.find_elements(
            By.CSS_SELECTOR, ".side_categories ul li ul li a"
        )[:5]
        categories = [
            (el.text.strip(), el.get_attribute("href"))
            for el in category_elements
            if el.get_attribute("href")
        ]
        for category_name, category_url in categories:
            if len(all_books) >= min_items:
                break
            driver.get(str(category_url))
            books = scrape_books_from_category(driver, wait, category_name)
            all_books.extend(books)
    except (TimeoutException, WebDriverException) as e:
        logger.error(f"Error durante el scraping: {e}")
    finally:
        driver.quit()
    return all_books
