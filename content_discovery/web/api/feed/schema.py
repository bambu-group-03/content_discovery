from pydantic import BaseModel, ConfigDict


class Tweet(BaseModel):
    """
    DTO for dummy models.

    It returned when accessing dummy models from the API.
    """
    author: str
    content: str


