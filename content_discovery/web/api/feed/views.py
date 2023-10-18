from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from sqlalchemy import inspect

from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.web.api.feed.schema import FeedPack, PostSnap, Tweet

router = APIRouter()

NON_EXISTENT = 405


@router.post("/post")
async def post_tweet(
    incoming_message: PostSnap,
    snaps_dao: SnapDAO = Depends(),
) -> Tweet:
    """Uploads a tweet with the received content."""
    snap = await snaps_dao.create_snaps_model(
        user_id=incoming_message.user_id,
        content=incoming_message.content,
    )
    insp = inspect(snap)
    i_d = insp.attrs.id.value
    return Tweet(
        id=i_d,
        author=str(insp.attrs.user_id.value),
        content=insp.attrs.content.value,
    )


@router.get("/tweet/{tweet_id}")
async def get_tweet(
    tweet_id: str,
    snaps_dao: SnapDAO = Depends(),
) -> Tweet:
    """Gets a tweet."""
    tweet = await snaps_dao.get_snap_from_id(tweet_id)
    if tweet:
        return Tweet(id=tweet.id, author=str(tweet.user_id), content=tweet.content)
    raise HTTPException(status_code=NON_EXISTENT, detail="That tweet doesnt exist")


@router.get("/")
async def get_tweets(
    user_id: str,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of tweet ids."""
    my_tweets = []

    # TODO: get list of users that user_id follows
    # from different microservice (identity socializer)
    # TEMP:
    followed_users = [user_id]
    for i_d in followed_users:
        snaps = await snaps_dao.get_from_user(i_d, 100, 0)
        for snap in iter(snaps):
            my_tweets.append(
                Tweet(id=snap.id, author=str(snap.user_id), content=snap.content),
            )
    return FeedPack(tweets=my_tweets)
