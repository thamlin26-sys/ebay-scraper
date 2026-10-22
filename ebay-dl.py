import argparse
import json
import os
import re
import time
from bs4 import BeautifulSoup
import requests


def parse_price(price_str):
    """
    Parses a price string into cents.
    Returns None if no price is found.
    """
    if not price_str:
        return None

    match = re.search(r"\$([\d,]+\.?\d*)", price_str)
    if match:
        clean_price = match.group(1).replace(",", "")
        try:
            return int(round(float(clean_price) * 100))
        except ValueError:
            return None
    return None


def parse_shipping(shipping_str):
    """
    Parses shipping string into cents.
    Returns 0 for free shipping, None if missing or unspecified.
    """
    if not shipping_str:
        return None

    shipping_lower = shipping_str.lower()
    if "free" in shipping_lower:
        return 0

    match = re.search(r"\$([\d,]+\.?\d*)", shipping_str)
    if match:
        clean_shipping = match.group(1).replace(",", "")
        try:
            return int(round(float(clean_shipping) * 100))
        except ValueError:
            return None

    return None


def parse_items_sold(sold_str):
    """
    Parses items sold count (e.g., "15 sold", "1,234 sold").
    Returns None if missing.
    """
    if not sold_str:
        return None

    match = re.search(r"([\d,]+)\s+(?:sold|purchased)", sold_str, re.IGNORECASE)
    if match:
        clean_num = match.group(1).replace(",", "")
        try:
            return int(clean_num)
        except ValueError:
            return None

    return None


def extract_items_from_html(html_content):
    """
    Extracts item dictionaries from the provided HTML string.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    items = []

    listing_elements = soup.select(".s-item, li.s-item")

    for listing in listing_elements:
        title_elem = listing.select_one(".s-item__title")
        if not title_elem or "shop on ebay" in title_elem.text.lower():
            continue

        name = title_elem.text.strip() if title_elem else None

        # Price
        price_elem = listing.select_one(".s-item__price")
        price = parse_price(price_elem.text) if price_elem else None

        # Condition / Status
        status_elem = listing.select_one(
            ".s-item__subtitle, .SECONDARY_INFO, .s-item__condition"
        )
        status = status_elem.text.strip() if status_elem else None

        # Shipping
        shipping_elem = listing.select_one(
            ".s-item__shipping, .s-item__freeXDays"
        )
        shipping = parse_shipping(shipping_elem.text) if shipping_elem else None

        # Free Returns (Returns True if present & free, None if missing)
        returns_elem = listing.select_one(".s-item__free-returns")
        if returns_elem:
            free_returns = "free" in returns_elem.text.lower()
        else:
            free_returns = None

        # Items Sold
        sold_elem = listing.select_one(
            ".s-item__quantity-sold, .s-item__hotness, .s-item__additional-information"
        )
        items_sold = parse_items_sold(sold_elem.text) if sold_elem else None

        item_dict = {
            "name": name,
            "price": price,
            "status": status,
            "shipping": shipping,
            "free_returns": free_returns,
            "items_sold": items_sold,
        }
        items.append(item_dict)

    return items


def main():
    parser = argparse.ArgumentParser(description="Scrape eBay search results.")
    parser.add_argument(
        "positional_search", nargs="?", help="Search term as positional argument"
    )
    parser.add_argument(
        "--search", "--query", "--term", help="Search term as flag argument"
    )
    parser.add_argument(
        "--pages-dir",
        help="Directory containing practice HTML pages (page-1.html to page-10.html)",
    )
    args = parser.parse_args()

    search_term = args.search or args.positional_search
    if not search_term:
        parser.error("A search term must be provided.")

    all_items = []

    if args.pages_dir:
        for page_num in range(1, 11):
            file_path = os.path.join(args.pages_dir, f"page-{page_num}.html")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                    items = extract_items_from_html(html_content)
                    all_items.extend(items)
    else:
        base_url = "https://www.ebay.com/sch/i.html"
        headers = {"User-Agent": "Mozilla/5.0"}

        for page_num in range(1, 11):
            params = {"_nkw": search_term, "_pgn": page_num}
            try:
                response = requests.get(
                    base_url, params=params, headers=headers, timeout=10
                )
                response.raise_for_status()
                items = extract_items_from_html(response.text)
                all_items.extend(items)
                time.sleep(1)
            except requests.RequestException as e:
                print(f"Error requesting page {page_num}: {e}")
                break

    output_filename = f"{search_term}.json"

    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2)

    print(f"Saved {len(all_items)} items to {output_filename}")


if __name__ == "__main__":
    main()