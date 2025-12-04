"""Core logic for finding next books in series."""

from typing import Optional
from audiobookshelf import fetch_all_series, build_series_dict_from_series
from audible_api import search_series_books
from storage import should_update_series, update_series, get_all_next_books, detect_new_release
from config import EXCLUDED_SERIES


def find_next_book(series_name: str, owned_max: float, sample_asin: str) -> Optional[dict]:
    """
    Find the next book in a series after the owned_max.

    Args:
        series_name: Name of the series
        owned_max: Highest book number currently owned
        sample_asin: ASIN of a book in the series (for API lookup)

    Returns:
        Dict with next book info or None if not found
    """
    # Search for all books in the series
    all_books = search_series_books(series_name, sample_asin)

    if not all_books:
        return None

    # Find the next book after owned_max (skip fractional books like 1.5, 2.5)
    next_book = None
    for book in all_books:
        seq = book.get("sequence", 0)
        if seq != int(seq):
            continue
        if seq > owned_max:
            if next_book is None or seq < next_book.get("sequence", float("inf")):
                next_book = book

    return next_book


def process_all_series(force_update: bool = False) -> tuple[dict, list]:
    """
    Process all series and find next books.

    Args:
        force_update: If True, update all series regardless of cache

    Returns:
        Tuple of (all_series_dict, new_releases_list)
    """
    print("Fetching series from AudioBookShelf...")
    series_list = fetch_all_series()
    print(f"Found {len(series_list)} series in library")

    series_dict = build_series_dict_from_series(series_list)
    print(f"Processed {len(series_dict)} series with valid ASINs")

    updated_count = 0
    skipped_count = 0
    new_releases = []

    for series_name, data in series_dict.items():
        # Skip excluded series
        if series_name in EXCLUDED_SERIES:
            print(f"  Skipping excluded series: {series_name}")
            skipped_count += 1
            continue

        owned_max = data["max_order"]
        sample_asin = data["sample_asin"]

        # Check if we need to update this series
        if not force_update and not should_update_series(series_name, owned_max):
            print(f"  Skipping (cached): {series_name}")
            skipped_count += 1
            continue

        print(f"  Processing: {series_name} (own up to #{owned_max})")

        # Find the next book
        next_book = find_next_book(series_name, owned_max, sample_asin)

        if next_book:
            print(f"    -> Next: #{next_book['sequence']} - {next_book['title']}")

            # Check if this is a new release (was null, now has a book)
            if detect_new_release(series_name, next_book):
                print(f"    ** NEW RELEASE! **")
                new_releases.append({
                    "series_name": series_name,
                    "asin": next_book["asin"],
                    "title": next_book["title"],
                    "sequence": next_book["sequence"],
                    "cover_url": next_book.get("cover_url", "")
                })
        else:
            print(f"    -> No next book found (series complete?)")

        # Update cache
        update_series(series_name, owned_max, next_book)
        updated_count += 1

    print(f"\nUpdated {updated_count} series, skipped {skipped_count}")

    if new_releases:
        print(f"New releases detected: {len(new_releases)}")

    return get_all_next_books(), new_releases


if __name__ == "__main__":
    # Test the module
    results, new_releases = process_all_series(force_update=True)

    if new_releases:
        print("\n" + "*" * 50)
        print("NEW RELEASES!")
        print("*" * 50)
        for release in new_releases:
            print(f"  {release['series_name']}: #{release['sequence']} - {release['title']}")

    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)

    for name, data in sorted(results.items()):
        next_book = data.get("next_book")
        if next_book:
            print(f"\n{name}")
            print(f"  Next: #{next_book['sequence']} - {next_book['title']}")
