"""Services for content_discovery."""


import httpx

from content_discovery.settings import settings


class Notification:
    """Send notifications."""

    def send_mention_notification(
        self,
        from_id: str,
        to_id: str,
        snap_id: str,
    ) -> None:
        """Send mention notification."""
        json_params = {
            "from_id": from_id,
            "to_id": to_id,
            "snap_id": snap_id,
        }

        try:
            httpx.post(_url_post_mention_notification(), json=json_params)
        except Exception as exc:
            print(str(exc))

    async def send_like_notification(
        self,
        from_id: str,
        to_id: str,
        snap_id: str,
    ) -> None:
        """Send like notification."""
        json_params = {
            "from_id": from_id,
            "to_id": to_id,
            "snap_id": snap_id,
        }

        try:
            await httpx.post(_url_post_like_notification(), json=json_params)
        except Exception as exc:
            print(str(exc))


def _url_post_mention_notification() -> str:
    return f"{settings.identity_socializer_url}/api/notification/new_mention"


def _url_post_like_notification() -> str:
    return f"{settings.identity_socializer_url}/api/notification/new_like"
