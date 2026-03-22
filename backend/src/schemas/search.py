from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class VideoIndexDocument(BaseModel):
    id: UUID = Field(..., description="Unique ID of the video (UUID)")
    name: str = Field(..., description="Video title", min_length=1)
    description: Optional[str] = Field(None, description="Video description")
    category: Optional[str] = Field(None, description="Category slug or name")
    channel_id: UUID = Field(..., description="Channel UUID")
    views: int = Field(0, description="Total number of views")


class VideoIndexMapping:
    """
    Defines the Elasticsearch mapping for the 'videos' index.
    """

    index_name = "videos"
    settings = {
        "analysis": {
            "analyzer": {
                "autocomplete_analyzer": {
                    "tokenizer": "autocomplete_tokenizer",
                    "filter": ["lowercase"],
                }
            },
            "tokenizer": {
                "autocomplete_tokenizer": {
                    "type": "edge_ngram",
                    "min_gram": 1,
                    "max_gram": 20,
                    "token_chars": ["letter", "digit"],
                }
            },
        }
    }
    mappings = {
        "properties": {
            "id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "autocomplete_analyzer",
                "search_analyzer": "standard",
            },
            "description": {"type": "text", "analyzer": "english"},
            "channel_id": {"type": "keyword"},
            "category": {"type": "keyword"},  # A single category
            "views": {"type": "integer"},
            # For the video hints/autocomplete feature
            "suggest_name": {
                "type": "completion",
                "analyzer": "standard",
                "search_analyzer": "standard",
                "preserve_separators": True,
                "preserve_position_increments": True,
                "max_input_length": 50,
            },
            # add ranker
            # https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/08-learning-to-rank.ipynb
            # vector field for hybrid search
            # set 'dims' to embedding model's dimensions
            # (e.g., 768 for SBERT, 1536 for OpenAI).
            # "video_embedding": {
            #     "type": "dense_vector",
            #     "dims": 768,  # <-- CHANGE ME
            #     "index": "true",
            #     "similarity": "cosine" # or 'dot_product' / 'l2_norm'
            # }
        }
    }


class VideoHintsResponse(BaseModel):
    hints: list[str]


class VideoResult(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    views: int


class VideoSearchResponse(BaseModel):
    results: list[VideoResult]


class VideoHintQuery(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Partial query string for video title suggestions.",
    )

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Search query cannot be empty")
        return v.strip()


class VideoSearchRequest(BaseModel):
    query: str = Field(
        ..., min_length=1, description="Search text input (e.g. 'funny cats')."
    )
    limit: int = Field(10, ge=1, le=50, description="Number of results to return.")
    smart_search: bool = Field(False, description="Enable hybrid vector + text search.")

    query_vector: Optional[List[float]] = Field(
        None, description="Vector embedding for semantic search."
    )

    category: Optional[str] = Field(None, description="Filter by category name.")
    min_views: Optional[int] = Field(None, ge=0, description="Minimum number of views.")
    max_views: Optional[int] = Field(None, ge=0, description="Maximum number of views.")
    has_description: bool = Field(
        False, description="Filter to only include videos that have a description."
    )

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Search query cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    @classmethod
    def check_views_range(cls, model):
        min_views = model.min_views
        max_views = model.max_views
        if min_views is not None and max_views is not None:
            if min_views > max_views:
                raise ValueError("min_views cannot be greater than max_views")
        return model
