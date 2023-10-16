from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from sqlalchemy import inspect

from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.web.api.feed.schema import FeedPack, PostSnap, Tweet

router = APIRouter()


@router.post("/post")
async def post_tweet(
    incoming_message: PostSnap,
    snaps_dao: SnapDAO = Depends(),
) -> Tweet:
    """
    uploads a tweet with the received content
    """
    snap = await snaps_dao.create_snaps_model(
        user_id=incoming_message.user_id, content=incoming_message.content
    )
    insp = inspect(snap)
    _id = insp.attrs.id.value
    return Tweet(
        id=_id, author=str(insp.attrs.user_id.value), content=insp.attrs.content.value
    )


@router.get("/tweet/{tweet_id}")
async def get_tweet(
    user_id: str,
    tweet_id: str,
    snaps_dao: SnapDAO = Depends(),
) -> None:
    """
    Gets a tweet
    """
    tweet = await snaps_dao.get_snap_from_id(tweet_id)
    if tweet:
        return Tweet(id=tweet.id, author=str(tweet.user_id), content=tweet.content)
    else:
        raise HTTPException(status_code=405, detail="That tweet doesnt exist")


@router.get("/")
async def get_tweets(
    user_id: int,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """
    Returns a list of tweet ids
    """
    _tweets = []

    # TODO: get list of users that user_id follows from different microservice (identity socializer)
    # TEMP:
    followed_users = [user_id]
    for _id in followed_users:
        snaps = await snaps_dao.get_from_user(_id, 100, 0)
        for snap in snaps:
            _tweets.append(
                Tweet(id=snap.id, author=str(snap.user_id), content=snap.content)
            )
    return FeedPack(tweets=_tweets)
