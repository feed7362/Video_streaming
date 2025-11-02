import uuid
from typing import Dict

from pydantic import BaseModel, Field


class ReactionRequest(BaseModel):
    reaction_name: str = Field(
        ...,
        description=(
            "Name of the reaction (must match an entry in `reaction_types` table). "
            "Examples: like, love, funny, dislike, angry"
        ),
        examples=["like", "love", "funny", "dislike", "angry"],
    )


class ReactionResponse(BaseModel):
    target_id: uuid.UUID
    target_type: str
    reactions: Dict[str, int]
