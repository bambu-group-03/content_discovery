
from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends

from content_discovery.web.api.feed.schema import Tweet, FeedPack, PostSnap
from content_discovery.db.dao.snaps_dao import SnapDAO

router = APIRouter()


@router.post("/post")
async def post_tweet(
    incoming_message: PostSnap, 
    snaps_dao: SnapDAO = Depends()) -> Tweet:
    """
    uploads a tweet with the received content
    """
    await snaps_dao.create_snaps_model(_content=incoming_message.content)
    return Tweet(id=42, author="Ada Lovelace", content=incoming_message.content)
    
@router.get("/tweet/{tweet_id}")
def get_tweet(tweet_id: int) -> None:
    """
    If the tweet id is 42, gets a tweet.
    """
    if(tweet_id == 42):
        return Tweet(id=42, author="Ada Lovelace", content="Hello! This is a tweet")
    else:
        raise HTTPException(status_code=405, detail="That tweet doesnt exist")

@router.get("/")
def get_tweets() -> None:
    """
    Returns a list of tweet ids
    """
    return FeedPack(tweets=[42])
