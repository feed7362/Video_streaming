import uuid
from typing import Protocol

from pydantic import BaseModel, Field


class ReactionModel(Protocol):
    user_id: uuid.UUID
    is_like: bool


class ReactionRequest(BaseModel):
    is_like: bool = Field(
        ...,
        description="Set to true for like or false for dislike",
        examples=[True, False],
    )


class ReactionResponse(BaseModel):
    video_id: uuid.UUID
    likes: int
    dislikes: int
