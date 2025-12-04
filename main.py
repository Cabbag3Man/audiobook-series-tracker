#!/usr/bin/env python3
"""
NewBooks - Find the next book in your Audible series.

Compares your AudioBookShelf library against Audible's catalog
to identify the next book in each series you're reading.
"""

import argparse
import sys
from next_book_finder import process_all_series
from storage import print_next_books, save_cache, load_cache
from notifications import notify_new_releases


def main():
    parser = argparse.ArgumentParser(
        description="Find the next book in your Audible series",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                  # Run with default settings (console + JSON)
    python main.py --console-only   # Only print to console, don't save
    python main.py --force          # Force update all series (ignore cache)
    python main.py --show           # Just show cached results
        """
    )

    parser.add_argument(
        "--console-only",
        action="store_true",
        help="Only output to console, don't save to JSON file"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update all series, ignoring cache"
    )

    parser.add_argument(
        "--show",
        action="store_true",
        help="Just show cached results without fetching new data"
    )

    args = parser.parse_args()

    try:
        if args.show:
            # Just display cached results
            print_next_books()
            return 0

        # Process all series
        print("=" * 60)
        print("NewBooks - Finding next books in your series")
        print("=" * 60)
        print()

        results, new_releases = process_all_series(force_update=args.force)

        # Output results (with new releases highlighted)
        print_next_books(results, new_releases)

        # Send notifications for new releases
        if new_releases:
            notify_new_releases(new_releases)

        # Save to file unless console-only mode
        if not args.console_only:
            cache = load_cache()
            cache["series"] = results
            cache["new_releases"] = new_releases
            save_cache(cache)
            print(f"\nResults saved to next_books.json")

        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
