from typing import List
from sqlalchemy import inspect
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
    snap = await snaps_dao.create_snaps_model(_content=incoming_message.content)
    insp = inspect(snap)
    _id = insp.attrs.id.value
    return Tweet(id=_id, author=str(insp.attrs.user_id.value), content=insp.attrs.content.value)
    
@router.get("/tweet/{tweet_id}")
async def get_tweet(tweet_id: int, snaps_dao: SnapDAO = Depends()) -> None:
    """
    Gets a tweet
    """
    tweet = await snaps_dao.filter(tweet_id)
    if(tweet):
        return Tweet(id=tweet.id, author=str(tweet.user_id), content=tweet.content)
    else:
        raise HTTPException(status_code=405, detail="That tweet doesnt exist")

@router.get("/")
async def get_tweets(snaps_dao: SnapDAO = Depends()) -> FeedPack:
    """
    Returns a list of tweet ids
    """
    _tweets = []
    snaps = await snaps_dao.get_all_snaps(100,0)
    for snap in snaps:
        _tweets.append(Tweet(id=snap.id, author=str(snap.user_id), content=snap.content))
    return FeedPack(tweets=_tweets)
