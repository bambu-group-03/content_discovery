from typing import List, Optional

from pydantic import BaseModel


class Tweet(BaseModel):
    """Tweet"""

    id: int
    author: str
    content: str


class FeedPack(BaseModel):
    """Collection of tweets"""

    tweets: Optional[List[Tweet]]


class PostSnap(BaseModel):
    """Snap posted by user"""

    user_id: int
    content: str
