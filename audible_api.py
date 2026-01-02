"""Audible API client for fetching product and series data."""

import os
import audible
from typing import Optional
from config import AUDIBLE_AUTH_FILE


# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_PATH = os.path.join(SCRIPT_DIR, AUDIBLE_AUTH_FILE)


def get_client() -> audible.Client:
    """Create an authenticated Audible client."""
    auth = audible.Authenticator.from_file(AUTH_PATH)
    return audible.Client(auth=auth)


def get_product(asin: str) -> Optional[dict]:
    """
    Fetch product details from Audible by ASIN.

    Uses catalog search with asins array - returns full data including
    series info and product images.

    Args:
        asin: The book's ASIN

    Returns:
        Product data dict or None if not found
    """
    try:
        with get_client() as client:
            response = client.get(
                "1.0/catalog/products",
                asins=[asin],
                response_groups="series,product_attrs,media"
            )
            products = response.get("products", [])
            return products[0] if products else None
    except Exception as e:
        print(f"Error fetching product {asin}: {e}")
        return None


def get_series_from_product(product: dict) -> list[dict]:
    """
    Extract series information from a product.

    Filters out:
    - merchant_title_authority relationships
    - Dramatized Adaptation sequences

    Returns:
        List of series dicts with: asin, title, sequence
    """
    series_list = []

    # Check the 'series' field first (cleaner data)
    for series in product.get("series", []):
        sequence = series.get("sequence", "")

        # Skip dramatized adaptations
        if "dramatized" in str(sequence).lower():
            continue

        try:
            seq_num = float(sequence) if sequence else 0
        except (ValueError, TypeError):
            continue

        series_list.append({
            "asin": series.get("asin"),
            "title": series.get("title"),
            "sequence": seq_num
        })

    # If no series found, check relationships
    if not series_list:
        for rel in product.get("relationships", []):
            rel_type = rel.get("relationship_type", "")

            # Only process series relationships
            if rel_type != "series":
                continue

            # Skip merchant_title_authority
            if rel.get("relationship_to_product") == "merchant_title_authority":
                continue

            sequence = rel.get("sequence", "")
            if "dramatized" in str(sequence).lower():
                continue

            try:
                seq_num = float(sequence) if sequence else 0
            except (ValueError, TypeError):
                continue

            series_list.append({
                "asin": rel.get("asin"),
                "title": rel.get("title"),
                "sequence": seq_num
            })

    return series_list


def get_series_products(series_asin: str) -> list[dict]:
    """
    Fetch all products in a series by the series ASIN.

    Args:
        series_asin: The series ASIN

    Returns:
        List of product dicts with basic info
    """
    try:
        with get_client() as client:
            response = client.get(
                f"1.0/catalog/products/{series_asin}",
                response_groups="product_attrs,media,series"
            )
            product = response.get("product", {})

            # For a series ASIN, the relationships contain the books
            books = []
            for rel in product.get("relationships", []):
                if rel.get("relationship_type") == "component":
                    books.append({
                        "asin": rel.get("asin"),
                        "sort": rel.get("sort", "0")
                    })

            # If we got books from relationships, fetch their details
            if books:
                detailed_books = []
                for book in books:
                    book_data = get_product(book["asin"])
                    if book_data:
                        detailed_books.append(book_data)
                return detailed_books

            return []
    except Exception as e:
        print(f"Error fetching series {series_asin}: {e}")
        return []


def search_series_books(series_name: str, sample_asin: str) -> list[dict]:
    """
    Find all books in a series starting from a sample book ASIN.

    Strategy:
    1. Get the sample product to find the series ASIN
    2. Use the series ASIN to get all books in the series

    Args:
        series_name: Name of the series (for matching)
        sample_asin: ASIN of a book we own in this series

    Returns:
        List of dicts with: asin, title, sequence, cover_url
    """
    # Get the sample product
    product = get_product(sample_asin)
    if not product:
        return []

    # Find the matching series
    series_info = get_series_from_product(product)
    target_series = None

    for s in series_info:
        # Try to match by name (case-insensitive, partial match)
        if s.get("title") and series_name.lower() in s["title"].lower():
            target_series = s
            break

    # If no match by name, take the first series
    if not target_series and series_info:
        target_series = series_info[0]

    if not target_series or not target_series.get("asin"):
        return []

    # Search for products in this series
    # Note: Audible API doesn't have a direct "get all books in series" endpoint
    # We'll use catalog search instead
    try:
        with get_client() as client:
            # Search by series title
            response = client.get(
                "1.0/catalog/products",
                num_results=50,
                products_sort_by="Relevance",
                title=target_series["title"],
                response_groups="series,product_attrs,media"
            )

            results = []
            for item in response.get("products", []):
                # Verify this book is actually in the series
                item_series = get_series_from_product(item)
                for s in item_series:
                    if s.get("asin") == target_series["asin"]:
                        # Get cover image from product_images in response
                        images = item.get("product_images", {})
                        cover_url = images.get("500", "")

                        results.append({
                            "asin": item.get("asin"),
                            "title": item.get("title"),
                            "sequence": s.get("sequence", 0),
                            "cover_url": cover_url,
                            "issue_date": item.get("issue_date", "")
                        })
                        break

            # Sort by sequence
            results.sort(key=lambda x: x["sequence"])
            return results

    except Exception as e:
        print(f"Error searching series '{series_name}': {e}")
        return []


if __name__ == "__main__":
    # Test the module
    test_asin = "B0FXY6DVJS"  # DCC Book 8
    print(f"Fetching product {test_asin}...")

    product = get_product(test_asin)
    if product:
        print(f"Title: {product.get('title')}")

        series = get_series_from_product(product)
        print(f"Series: {series}")

        if series:
            print(f"\nSearching for books in '{series[0]['title']}'...")
            books = search_series_books(series[0]["title"], test_asin)
            for book in books:
                print(f"  #{book['sequence']}: {book['title']} | Cover: {'YES' if book.get('cover_url') else 'NO'} | Issue: {book.get('issue_date', 'N/A')}")





