from fastapi import APIRouter, HTTPException
from content_discovery.web.api.feed.schema import Tweet

router = APIRouter()


@router.get("/tweet/{tweet_id}")
def get_tweet(tweet_id: int) -> None:
    """
    If the tweet id is 42, gets a tweet.
    """
    if(tweet_id == 42):
        return Tweet(author="Ada Lovelace", content="Hello! This is a tweet")
    else:
        raise HTTPException(status_code=405, detail="That tweet doesnt exist")
