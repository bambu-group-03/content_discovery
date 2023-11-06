import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Snap(BaseModel):
    """Snap"""

    id: uuid.UUID
    author: str
    content: str
    likes: int
    shares: int
    favs: int
    created_at: datetime
    parent_id: Optional[uuid.UUID]


class FeedPack(BaseModel):
    """Collection of snaps"""

    snaps: Optional[List[Snap]]


class PostSnap(BaseModel):
    """Snap posted by user"""

    user_id: str
    content: str


class PostReply(BaseModel):
    """Snap posted by user"""

    user_id: str
    parent_id: str
    content: str
