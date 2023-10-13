from pydantic import BaseModel
from typing import List, Optional

class Tweet(BaseModel):
    """
    Tweet
    """
    id: int
    author: str
    content: str


class FeedPack(BaseModel):
    """
    Collection of tweets
    """
    tweets: Optional[List[int]]

class PostSnap(BaseModel):
    """
    Snap posted by user
    """
    content: str


