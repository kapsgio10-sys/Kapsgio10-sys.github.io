import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import requests
from bs4 import BeautifulSoup


PRODUCTS_FILE = Path("products.json")
PRICES_FILE = Path("prices.json")


def normalize_price(text: str) -> str | None:
    """
    Παίρνει κείμενο τιμής και προσπαθεί να βγάλει καθαρή τιμή.
    Αν δεν βρει τιμή, επιστρέφει None.
    """
    if not text:
        return None

    text = text.strip().replace("\xa0", " ")

    match = re.search(r"(\d+[.,]?\d*)\s*€", text)
    if match:
        return match.group(0).replace(".", ",")

    match = re.search(r"€\s*(\d+[.,]?\d*)", text)
    if match:
        return match.group(1).replace(".", ",") + "€"

    return None


def fetch_price_from_page(url: str, selector: str) -> str | None:
    """
    Τραβάει τιμή από σελίδα μόνο αν υπάρχει URL και CSS selector.
    Δεν μαντεύει. Αν αποτύχει, επιστρέφει None.
    """
    if not url or not selector:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; GadgetoraPriceBot/1.0)"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    element = soup.select_one(selector)

    if not element:
        return None

    return normalize_price(element.get_text(" ", strip=True))


def load_products() -> list[dict]:
    with PRODUCTS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get("products", [])


def main() -> None:
    products = load_products()
    prices = {}

    for product in products:
        product_id = product["id"]
        store = product.get("store", "-")
        price_url = product.get("price_source_url", "")
        selector = product.get("price_selector", "")

        try:
            price = fetch_price_from_page(price_url, selector)

            if price:
                prices[product_id] = {
                    "price": price,
                    "store": store,
                    "status": "ok"
                }
            else:
                prices[product_id] = {
                    "price": "Δες διαθέσιμες τιμές",
                    "store": store,
                    "status": "no_price_source"
                }

        except Exception as error:
            prices[product_id] = {
                "price": "Δες διαθέσιμες τιμές",
                "store": store,
                "status": "error",
                "error": str(error)
            }

    output = {
        "updated_at": datetime.now(ZoneInfo("Europe/Athens")).isoformat(),
        "prices": prices
    }

    with PRICES_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    print("Updated prices.json")


if __name__ == "__main__":
    main()
