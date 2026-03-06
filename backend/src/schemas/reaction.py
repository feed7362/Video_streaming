import uuid
from typing import Dict, Literal

from pydantic import BaseModel, Field, field_validator


class ReactionRequest(BaseModel):
    reaction_name: Literal[
        "like",
        "dislike",
    ] = Field(..., description="The type of reaction the user is applying.")

    @field_validator("reaction_name")
    @classmethod
    def must_be_like_or_dislike(cls, v: str) -> str:
        if v not in {"like", "dislike"}:
            raise ValueError("reaction_name must be 'like' or 'dislike'")
        return v


class ReactionResponse(BaseModel):
    target_id: uuid.UUID
    target_type: str
    reactions: Dict[str, int]
