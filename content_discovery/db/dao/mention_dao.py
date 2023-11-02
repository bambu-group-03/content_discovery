import re
import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.mention_model import MentionModel


class MentionDAO:
    """Class for accessing mentions table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_mention_model(self, snap_id: uuid.UUID, username: str) -> None:
        """Add single mention to session."""
        try:
            mention = MentionModel(snap_id=snap_id, mentioned_username=username)
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
                await self.create_mention_model(snap_id, mention)
