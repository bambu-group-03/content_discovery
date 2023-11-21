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
    username: Optional[str]
    fullname: Optional[str]
    parent_id: Optional[uuid.UUID]
    visibility: int
    privacy: int
    has_shared: Optional[bool] = False
    has_liked: Optional[bool] = False
    num_replies: Optional[int] = 0
    profile_photo_url: Optional[str] = None
    is_shared_by: List[str] = []


class FeedPack(BaseModel):
    """Collection of snaps"""

    snaps: Optional[List[Snap]]


class PostSnap(BaseModel):
    """Snap posted by user"""

    user_id: str
    content: str
    privacy: int


class ReplySnap(BaseModel):
    """Snap posted by user"""

    user_id: str
    parent_id: str
    content: str


class UpdateSnap(BaseModel):
    """Snap posted by user"""

    user_id: str
    snap_id: str
    content: str
