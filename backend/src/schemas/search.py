from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


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
    category: list[str] | None = None
    views: int


class VideoSearchResponse(BaseModel):
    results: list[VideoResult]
