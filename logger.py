"""Centralized logging module for NewBooks project."""

import os
from datetime import datetime

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")

# Global log file handle
_log_file = None
_log_path = None


def init_log():
    """Initialize the log file for today's date."""
    global _log_file, _log_path

    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    # Create log file with today's date
    today = datetime.now().strftime("%Y-%m-%d")
    _log_path = os.path.join(LOG_DIR, f"{today}.log")

    # Open in append mode
    _log_file = open(_log_path, "a", encoding="utf-8")


def log(process: str, message: str):
    """
    Write a timestamped log entry.

    Args:
        process: The process/module name (e.g., 'main', 'finder', 'notifications')
        message: The log message
    """
    if _log_file is None:
        init_log()

    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}][{process}] - {message}\n"
    _log_file.write(entry)
    _log_file.flush()


def log_error(process: str, message: str):
    """
    Write an error log entry.

    Args:
        process: The process/module name
        message: The error message
    """
    log(process, f"ERROR: {message}")


def log_header():
    """Write the log header block with current date."""
    if _log_file is None:
        init_log()

    today = datetime.now().strftime("%Y-%m-%d")
    header = f"\n{'#' * 44}\n# {today}\n{'#' * 44}\n"
    _log_file.write(header)
    _log_file.flush()


def log_footer():
    """Write the log footer block."""
    if _log_file is None:
        return

    footer = f"{'#' * 44}\n# End\n{'#' * 44}\n"
    _log_file.write(footer)
    _log_file.flush()


def close_log():
    """Close the log file."""
    global _log_file
    if _log_file:
        _log_file.close()
        _log_file = None


if __name__ == "__main__":
    # Test the module
    init_log()
    log_header()
    log("main", "Script started")
    log("finder", "Processing: Test Series")
    log("finder", "Next book found: #5 - Test Book (Release: 2026-01-13)")
    log_error("notifications", "Failed to send notification - Connection timeout")
    log("main", "Script completed")
    log_footer()
    close_log()
    print(f"Test log written to: {_log_path}")
