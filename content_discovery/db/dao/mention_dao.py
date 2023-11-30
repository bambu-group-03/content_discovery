import re
import uuid
from typing import List

import httpx
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.constants import Visibility
from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.mention_model import MentionModel
from content_discovery.db.models.snaps_model import SnapsModel
from content_discovery.settings import settings


class MentionDAO:
    """Class for accessing mentions table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_mention_model(
        self,
        snap_id: uuid.UUID,
        username: str,
        user_id: str,
    ) -> None:
        """Add single mention to session."""
        try:
            mention = MentionModel(
                snap_id=snap_id,
                mentioned_username=username,
                mentioned_id=user_id,
            )
            self.session.add(mention)

            return

        except Exception:
            return

    async def create_mentions(
        self,
        snap_id: uuid.UUID,
        content: str,
    ) -> None:
        """Create mentions from snap content."""
        if "@" in content:
            mentions = re.findall(r"(?:^|\s)(@\w+)", content)

            for mention in mentions:
                # Remove @ from mention
                mention = mention[1:]

                user_id = self.get_user_info_by_username(mention)

                await self.create_mention_model(snap_id, mention, user_id)

    async def get_mentions(
        self,
        user_id: str,
    ) -> List[SnapsModel]:
        """Get list of filtered snaps by mention."""
        query = select(SnapsModel).distinct()
        query = query.where(SnapsModel.visibility == Visibility.PUBLIC.value)
        query = query.join(MentionModel.snap)
        query = query.where(MentionModel.mentioned_id == user_id)

        rows = await self.session.execute(query)
        print(user_id)
        return list(rows.scalars().fetchall())

    def get_user_info_by_username(self, username: str) -> str:
        """Returns user_id from username."""
        try:
            author = httpx.get(_url_get_user_info_by_username(username)).json()

            return author["id"]
        except Exception:
            return "unknown"


def _url_get_user_info_by_username(username: str) -> str:
    return f"{settings.identity_socializer_url}/api/auth/user_by_username/{username}"
