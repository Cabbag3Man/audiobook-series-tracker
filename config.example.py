"""
Configuration constants for NewBooks project.

Copy this file to config.py and fill in your values:
    cp config.example.py config.py

Never commit config.py to version control - it contains sensitive API keys!
"""

# =============================================================================
# AUDIOBOOKSHELF SETTINGS
# =============================================================================

# Base URL of your AudioBookShelf server
# Example: "http://192.168.1.100:13378" or "https://abs.yourdomain.com"
# Find this in your browser's address bar when accessing AudioBookShelf
ABS_BASE_URL = ""

# Library ID - the UUID of the library containing your audiobooks
# How to find it:
#   1. Open AudioBookShelf in your browser
#   2. Navigate to the library you want to use
#   3. Look at the URL: http://your-server/library/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
#   4. The UUID after /library/ is your Library ID
# Example: "35737281-986f-43e6-aaff-bb92e685ce6c"
ABS_LIBRARY_ID = ""

# API Key for authentication
# How to create one:
#   1. Open AudioBookShelf and log in
#   2. Click your user icon (top right) > Settings
#   3. Scroll to "API Tokens" section
#   4. Click "Create Token", give it a name (e.g., "NewBooks")
#   5. Copy the generated token (starts with "eyJ...")
# Example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
ABS_API_KEY = ""


# =============================================================================
# AUDIBLE API SETTINGS
# =============================================================================

# Path to your Audible authentication file (relative to this script)
#
# There are two ways to create this file:
#
# -----------------------------------------------------------------------------
# OPTION 1: Using the audible Python library (recommended)
# -----------------------------------------------------------------------------
# Run this Python code once to generate the auth file:
#
#   import audible
#   auth = audible.Authenticator.from_login(
#       "your_email@example.com",    # Your Amazon/Audible email
#       "your_password",              # Your Amazon/Audible password
#       locale="us",                  # Your marketplace: us, uk, de, fr, au, ca, jp, it, in, es
#       with_username=False
#   )
#   auth.to_file("audible_auth.json")
#
# Note: You may be prompted for 2FA/OTP if enabled on your account.
# Locales: us, uk, de, fr, au, ca, jp, it, in, es
#
# -----------------------------------------------------------------------------
# OPTION 2: Using audible-cli (command line tool)
# -----------------------------------------------------------------------------
#   1. Install: pip install audible-cli
#   2. Run: audible quickstart
#   3. Follow the prompts to log in
#   4. Copy the generated auth file to this directory
#
# -----------------------------------------------------------------------------
# The auth file contains encrypted credentials - keep it safe and never commit!
AUDIBLE_AUTH_FILE = "audible_auth.json"


# =============================================================================
# OUTPUT SETTINGS
# =============================================================================

# JSON file where results are cached
# This file stores:
#   - Series data and highest owned book numbers
#   - Next book information for each series
#   - New release history
# The cache prevents unnecessary API calls on subsequent runs
OUTPUT_FILE = "next_books.json"


# =============================================================================
# SERIES EXCLUSIONS
# =============================================================================

# List of series names to skip when checking for next books
# Useful for:
#   - Series you've abandoned and don't want notifications for
#   - Series with irregular numbering that causes issues
#   - Completed series where you own all books
# Example: ["Tamer", "Some Other Series"]
EXCLUDED_SERIES = []


# =============================================================================
# NOTIFICATION SETTINGS
# =============================================================================

# Discord Webhook URL for new release notifications
# Leave empty ("") to disable Discord notifications
#
# How to create a Discord webhook:
#   1. Open Discord and go to your server
#   2. Click the gear icon next to a channel name (Edit Channel)
#   3. Go to Integrations > Webhooks
#   4. Click "New Webhook"
#   5. Give it a name (e.g., "NewBooks Bot")
#   6. Optionally set an avatar
#   7. Click "Copy Webhook URL"
#   8. Paste the URL below
#
# Example: "https://discord.com/api/webhooks/123456789/abcdefg..."
DISCORD_WEBHOOK_URL = ""
