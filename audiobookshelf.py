"""AudioBookShelf API client for fetching library and series data."""

import re
import requests
from typing import Optional
from config import ABS_BASE_URL, ABS_LIBRARY_ID, ABS_API_KEY
from logger import log, log_error


def get_headers() -> dict:
    """Get authorization headers for API requests."""
    return {"Authorization": f"Bearer {ABS_API_KEY}"}


def fetch_library_series(limit: int = 100, page: int = 0) -> dict:
    """
    Fetch series from AudioBookShelf library.

    Args:
        limit: Results per page (must be > 0)
        page: Page number (0-indexed)

    Returns:
        API response with results array and total count
    """
    url = f"{ABS_BASE_URL}/api/libraries/{ABS_LIBRARY_ID}/series"
    params = {"limit": limit, "page": page}

    try:
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log_error("audiobookshelf", f"API request failed: {e}")
        raise


def fetch_all_series() -> list:
    """Fetch all series with pagination."""
    all_series = []
    page = 0
    limit = 100

    log("audiobookshelf", "Fetching series from AudioBookShelf...")

    while True:
        data = fetch_library_series(limit=limit, page=page)
        results = data.get("results", [])
        all_series.extend(results)

        # Check if we have more pages
        total = data.get("total", 0)
        if len(all_series) >= total or not results:
            break
        page += 1

    log("audiobookshelf", f"Found {len(all_series)} series in library")
    return all_series


def extract_asin_from_path(path: str) -> Optional[str]:
    """
    Extract ASIN from file path.

    Path format: D:/Audible/<bookname>_<asin>_<codec>.m4b
    Example: D:/Audible/The Beginning After _1774241307_LC_128_44100_Stereo.m4b
    """
    if not path:
        return None

    # Match pattern: _<ASIN>_LC_ (codec always starts with LC_)
    # ASIN can be alphanumeric (e.g., 1774241307, B008GV0PSM)
    match = re.search(r'_([A-Z0-9]{10})_LC_', path, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def parse_series_info(series_name: str) -> tuple[str, float]:
    """
    Parse series name and order from seriesName field.

    Format: "Series Name #1" or "Series Name #1.5"
    For Publisher's Packs like "Series Name #1-2", returns the highest number.

    Returns:
        Tuple of (series_name, series_order)
    """
    if not series_name:
        return ("", 0)

    # Match pattern: "Series Name #X" or "Series Name #X-Y" or "Series Name #X.Y"
    match = re.match(r'^(.+?)\s*#(\d+(?:\.\d+)?(?:-(\d+(?:\.\d+)?))?)$', series_name.strip())
    if match:
        name = match.group(1).strip()
        order_str = match.group(2)

        # Handle ranges like "1-2" - take the highest
        if '-' in order_str:
            parts = order_str.split('-')
            order = max(float(p) for p in parts)
        else:
            order = float(order_str)

        return (name, order)

    return (series_name.strip(), 0)


def get_book_series_data(item: dict) -> list[dict]:
    """
    Extract series data from a library item.

    Returns list of dicts with: asin, series_name, series_order
    A book can belong to multiple series (comma-separated).
    """
    results = []

    media = item.get("media", {})
    metadata = media.get("metadata", {})

    # Get ASIN from metadata or file path
    asin = metadata.get("asin")
    if not asin:
        path = item.get("path", "")
        asin = extract_asin_from_path(path)

    if not asin:
        return results

    # Get series name(s) - can be comma-separated for multiple series
    series_name_raw = metadata.get("seriesName", "")
    if not series_name_raw:
        return results

    # Split by comma for books in multiple series
    series_entries = [s.strip() for s in series_name_raw.split(",")]

    for series_entry in series_entries:
        name, order = parse_series_info(series_entry)
        if name:
            results.append({
                "asin": asin,
                "series_name": name,
                "series_order": order,
                "title": metadata.get("title", "Unknown")
            })

    return results


def build_series_dict_from_series(series_list: list) -> dict:
    """
    Build a dictionary of series from the ABS series endpoint data.

    Args:
        series_list: List of series objects from /api/libraries/<id>/series

    Returns:
        Dict mapping series_name -> {max_order: float, sample_asin: str, books: list}
    """
    series_dict = {}

    for series in series_list:
        series_name = series.get("name", "")
        if not series_name:
            continue

        books_data = []
        max_order = 0
        sample_asin = None

        for book in series.get("books", []):
            # Get book metadata
            media = book.get("media", {})
            metadata = media.get("metadata", {})

            # Get ASIN from metadata or file path
            asin = metadata.get("asin")
            if not asin:
                path = book.get("path", "")
                asin = extract_asin_from_path(path)

            if not asin:
                continue

            # Get series order from seriesName field
            series_name_field = metadata.get("seriesName", "")

            # Find the order for THIS series (book might be in multiple series)
            order = 0
            for entry in series_name_field.split(","):
                entry = entry.strip()
                parsed_name, parsed_order = parse_series_info(entry)
                if parsed_name.lower() == series_name.lower():
                    order = parsed_order
                    break
                # Also try partial match
                if series_name.lower() in parsed_name.lower() or parsed_name.lower() in series_name.lower():
                    order = parsed_order

            if order > max_order:
                max_order = order
                sample_asin = asin

            if sample_asin is None:
                sample_asin = asin

            books_data.append({
                "asin": asin,
                "order": order,
                "title": metadata.get("title", "Unknown")
            })

        if sample_asin:
            series_dict[series_name] = {
                "max_order": max_order,
                "sample_asin": sample_asin,
                "books": books_data
            }

    return series_dict


if __name__ == "__main__":
    # Test the module
    print("Fetching series from AudioBookShelf...")
    series_list = fetch_all_series()
    print(f"Found {len(series_list)} series")

    series_dict = build_series_dict_from_series(series_list)
    print(f"\nProcessed {len(series_dict)} series:")
    for name, data in sorted(series_dict.items()):
        print(f"  {name}: max #{data['max_order']} ({len(data['books'])} books)")

