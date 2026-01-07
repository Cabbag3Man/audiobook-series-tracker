"""Notification module for sending alerts about new releases."""

import requests
from config import DISCORD_WEBHOOK_URL
from logger import log, log_error


def send_discord_notification(new_releases: list) -> bool:
    """
    Send a Discord webhook notification for new releases.

    Args:
        new_releases: List of new release dicts with series_name, title, sequence, asin

    Returns:
        True if notification sent successfully
    """
    if not DISCORD_WEBHOOK_URL:
        return False

    if not new_releases:
        return False

    # Build the embed message
    embeds = []
    for release in new_releases:
        embed = {
            "title": "New Audiobook Released!",
            "description": f"**{release['series_name']}** Book #{release['sequence']}: {release['title']}\n\n[View on Audible](https://www.audible.com/pd/{release['asin']})",
            "color": 5814783,  # Blue color
            "url": f"https://www.audible.com/pd/{release['asin']}"
        }

        # Add cover art if available
        cover_url = release.get("cover_url", "")
        if cover_url:
            embed["image"] = {"url": cover_url}

        embeds.append(embed)

    # Discord allows max 10 embeds per message
    # Split into batches if needed
    for i in range(0, len(embeds), 10):
        batch = embeds[i:i+10]
        payload = {
            "username": "NewBooks",
            "embeds": batch
        }

        try:
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error sending Discord notification: {e}")
            log_error("notifications", f"Failed to send Discord notification: {e}")
            return False

    print(f"Discord notification sent for {len(new_releases)} new release(s)")
    log("notifications", f"Discord notification sent: {len(new_releases)} new release(s)")
    return True


def send_releasing_today_notification(releases: list) -> bool:
    """
    Send a Discord webhook notification for books releasing today.

    Args:
        releases: List of release dicts with series_name, title, sequence, asin, issue_date

    Returns:
        True if notification sent successfully
    """
    if not DISCORD_WEBHOOK_URL:
        return False

    if not releases:
        return False

    # Build the embed message
    embeds = []
    for release in releases:
        embed = {
            "title": "Book Releasing Today!",
            "description": f"**{release['series_name']}** Book #{release['sequence']}: {release['title']}\n\n[View on Audible](https://www.audible.com/pd/{release['asin']})",
            "color": 3066993,  # Green color
            "url": f"https://www.audible.com/pd/{release['asin']}"
        }

        # Add cover art if available
        cover_url = release.get("cover_url", "")
        if cover_url:
            embed["image"] = {"url": cover_url}

        embeds.append(embed)

    # Discord allows max 10 embeds per message
    for i in range(0, len(embeds), 10):
        batch = embeds[i:i+10]
        payload = {
            "username": "NewBooks",
            "embeds": batch
        }

        try:
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error sending Discord notification: {e}")
            log_error("notifications", f"Failed to send releasing today notification: {e}")
            return False

    print(f"Discord notification sent for {len(releases)} book(s) releasing today")
    log("notifications", f"Discord notification sent: {len(releases)} book(s) releasing today")
    return True


def notify_releasing_today(releases: list) -> None:
    """
    Send notifications for books releasing today via all configured channels.

    Args:
        releases: List of release dicts
    """
    if not releases:
        return

    # Discord
    if DISCORD_WEBHOOK_URL:
        send_releasing_today_notification(releases)


def notify_new_releases(new_releases: list) -> None:
    """
    Send notifications for new releases via all configured channels.

    Args:
        new_releases: List of new release dicts
    """
    if not new_releases:
        return

    # Discord
    if DISCORD_WEBHOOK_URL:
        send_discord_notification(new_releases)


if __name__ == "__main__":
    # Test the module
    test_releases = [
        {
            "series_name": "Dungeon Crawler Carl",
            "title": "A Parade of Horribles",
            "sequence": 8,
            "asin": "B0FXY6DVJS",
            "cover_url": "https://m.media-amazon.com/images/I/91hNI-NNERL._SL500_.jpg"
        },
        {
            "series_name": "He Who Fights with Monsters",
            "title": "Book 10",
            "sequence": 10,
            "asin": "B0C1PV6Q7C",
            "cover_url": ""
        }
    ]

    if DISCORD_WEBHOOK_URL:
        print("Sending test notification...")
        send_discord_notification(test_releases)
    else:
        print("DISCORD_WEBHOOK_URL not configured in config.py")
        print("Add your webhook URL to test notifications")
