"""Services for content_discovery."""

import httpx

from content_discovery.settings import settings


class Notification:
    """Send notifications."""

    def send_notification(self, user_id: str, title: str, content: str) -> None:
        """Send notification."""
        json_params = {
            "user_id": user_id,
            "title": title,
            "content": content,
        }
        try:
            httpx.post(_url_post_notification(), json=json_params)
        except Exception as exc:
            print(str(exc))


def _url_post_notification() -> str:
    return f"{settings.identity_socializer_url}/api/notification/"
