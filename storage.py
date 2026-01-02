"""Storage module for caching and persisting next book data."""

import json
import os
from datetime import datetime
from typing import Optional
from config import OUTPUT_FILE


# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, OUTPUT_FILE)


def load_cache() -> dict:
    """Load the cached next books data."""
    if not os.path.exists(OUTPUT_PATH):
        return {"last_updated": None, "series": {}}

    try:
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading cache: {e}")
        return {"last_updated": None, "series": {}}


def save_cache(data: dict) -> None:
    """Save the next books data to cache."""
    data["last_updated"] = datetime.now().isoformat()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_cached_series(series_name: str) -> Optional[dict]:
    """Get cached data for a specific series."""
    cache = load_cache()
    return cache.get("series", {}).get(series_name)


def should_update_series(series_name: str, current_max_order: float) -> bool:
    """
    Check if a series needs to be updated.

    Returns True if:
    - Series is not in cache
    - Current max order is higher than cached max order
    """
    cached = get_cached_series(series_name)
    if not cached:
        return True

    cached_max = cached.get("owned_max", 0)
    return current_max_order > cached_max


def update_series(series_name: str, owned_max: float, next_book: Optional[dict]) -> None:
    """
    Update the cache for a specific series.

    Args:
        series_name: Name of the series
        owned_max: Highest book number owned
        next_book: Dict with next book info (asin, title, sequence, cover_url) or None
    """
    cache = load_cache()

    if "series" not in cache:
        cache["series"] = {}

    cache["series"][series_name] = {
        "owned_max": owned_max,
        "next_book": next_book
    }

    save_cache(cache)


def get_all_next_books() -> dict:
    """Get all cached next books data."""
    cache = load_cache()
    return cache.get("series", {})


def detect_new_release(series_name: str, new_next_book: Optional[dict]) -> bool:
    """
    Check if a series has a new release (went from null to having a next book).

    Args:
        series_name: Name of the series
        new_next_book: The newly found next book (or None)

    Returns:
        True if this is a new release
    """
    if not new_next_book:
        return False

    cached = get_cached_series(series_name)
    if not cached:
        return False  # New series, not a "new release"

    old_next_book = cached.get("next_book")
    # New release if we had no next book before, but now we do
    return old_next_book is None


def get_new_releases() -> list:
    """Get the list of new releases from the cache."""
    cache = load_cache()
    return cache.get("new_releases", [])


def save_new_releases(releases: list) -> None:
    """Save new releases to the cache."""
    cache = load_cache()
    cache["new_releases"] = releases
    save_cache(cache)


def get_releasing_today() -> list:
    """
    Check all cached series for books releasing today.

    Returns:
        List of dicts with series_name and next_book info for books releasing today
    """
    today = datetime.now().strftime("%Y-%m-%d")
    cache = load_cache()
    releasing_today = []

    for series_name, data in cache.get("series", {}).items():
        next_book = data.get("next_book")
        if next_book and next_book.get("issue_date") == today:
            releasing_today.append({
                "series_name": series_name,
                "asin": next_book.get("asin", ""),
                "title": next_book.get("title", ""),
                "sequence": next_book.get("sequence", 0),
                "cover_url": next_book.get("cover_url", ""),
                "issue_date": next_book.get("issue_date", "")
            })

    return releasing_today


def print_new_releases(releases: list) -> None:
    """Print new releases prominently."""
    if not releases:
        return

    print("\n" + "*" * 60)
    print("NEW RELEASES DETECTED!")
    print("*" * 60)

    for release in releases:
        print(f"\n  {release['series_name']}")
        print(f"    Book #{release['sequence']}: {release['title']}")
        print(f"    ASIN: {release['asin']}")

    print("\n" + "*" * 60)


def print_next_books(data: Optional[dict] = None, new_releases: Optional[list] = None) -> None:
    """Print next books in a formatted way."""
    # Print new releases first if any
    if new_releases:
        print_new_releases(new_releases)

    if data is None:
        data = get_all_next_books()

    if not data:
        print("No next books found.")
        return

    print("\n" + "=" * 60)
    print("NEXT BOOKS IN YOUR SERIES")
    print("=" * 60)

    # Sort by series name
    for series_name in sorted(data.keys()):
        info = data[series_name]
        next_book = info.get("next_book")

        print(f"\n{series_name}")
        print(f"  Currently own up to: #{info.get('owned_max', '?')}")

        if next_book:
            print(f"  Next book: #{next_book.get('sequence')} - {next_book.get('title')}")
            print(f"  ASIN: {next_book.get('asin')}")
            if next_book.get("issue_date"):
                print(f"  Release date: {next_book.get('issue_date')}")
            if next_book.get("cover_url"):
                print(f"  Cover: {next_book.get('cover_url')}")
        else:
            print("  No next book available (series complete or not found)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Test the module
    print("Testing storage module...")

    # Test update
    update_series(
        "Test Series",
        owned_max=3,
        next_book={
            "asin": "B0TEST123",
            "title": "Test Book 4",
            "sequence": 4,
            "cover_url": "https://example.com/cover.jpg"
        }
    )

    # Test print
    print_next_books()

    # Clean up test data
    cache = load_cache()
    if "Test Series" in cache.get("series", {}):
        del cache["series"]["Test Series"]
        save_cache(cache)
        print("\nTest data cleaned up.")
