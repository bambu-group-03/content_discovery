import uuid
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


class FeedPack(BaseModel):
    """Collection of snaps"""

    snaps: Optional[List[Snap]]


class PostSnap(BaseModel):
    """Snap posted by user"""

    user_id: str
    content: str
