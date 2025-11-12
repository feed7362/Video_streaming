from typing import Any, List, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from ..infrastructure.elasticsearch import get_es_client
from ..schemas.endpoint import ErrorResponse
from ..schemas.search import VideoHintsResponse, VideoResult, VideoSearchResponse

router_search = APIRouter(
    prefix="/api/search",
    tags=["search"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


# ─────────────────────────────────────────────────────────────
# 🔎 Autocomplete (completion suggester + fuzzy fallback)
# ─────────────────────────────────────────────────────────────
@router_search.get(
    "/video_hints",
    response_model=VideoHintsResponse,
    summary="Get live suggestions for video search",
    description="Returns top matching video names while the user types. "
    "Uses Elasticsearch completion suggester.",
    response_description="List of suggested video names.",
    responses={
        200: {
            "model": VideoHintsResponse,
            "description": "Suggestions successfully retrieved.",
        },
        400: {"model": ErrorResponse, "description": "Invalid query or parameters."},
        500: {"model": ErrorResponse, "description": "Unexpected server error."},
    },
)
async def get_hints(
    q: str = Query(
        ...,
        min_length=1,
        description="Partial query string for video title suggestions.",
    ),
    es: AsyncElasticsearch = Depends(get_es_client),
) -> VideoHintsResponse:
    """
    Returns autocomplete hints for the user's partial query.
    Uses Elasticsearch completion suggester.
    """
    suggest_query = {
        "video-suggest": {
            "prefix": q,
            "completion": {
                "field": "suggest_name",
                "skip_duplicates": True,
                "fuzzy": {"fuzziness": 1},
                "size": 10,
            },
        }
    }

    response = await es.search(index="videos", suggest=suggest_query)

    options = response["suggest"]["video-suggest"][0]["options"]
    hints = [opt.get("_source", {}).get("name") or opt.get("text") for opt in options]
    hints = [h for h in hints if h]
    return VideoHintsResponse(hints=hints)


@router_search.post(
    "/video",
    response_model=VideoSearchResponse,
    summary="Hybrid video search",
    description="""
    Performs full-text or hybrid (text + vector) video search.

    - Uses `multi_match` query for text relevance (title, description, category).
    - Optionally uses vector embeddings for semantic similarity.
    - Supports filters for category, view count range, and description presence.
    """,
    response_description="List of matched video results.",
    responses={
        200: {
            "model": VideoSearchResponse,
            "description": "Search results retrieved successfully.",
        },
        400: {"model": ErrorResponse, "description": "Invalid request or parameters."},
        500: {"model": ErrorResponse, "description": "Unexpected error occurred."},
    },
)
async def video_search(
    q: str = Query(
        ..., min_length=1, description="Search text input (e.g. 'funny cats')."
    ),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return."),
    smart_search: bool = Query(
        False, description="Enable hybrid vector + text search."
    ),
    query_vector: Optional[List[float]] = Query(
        None, description="Vector embedding for semantic search."
    ),
    category: Optional[str] = Query(None, description="Filter by category name."),
    min_views: Optional[int] = Query(
        None, ge=0, description="Minimum number of views."
    ),
    max_views: Optional[int] = Query(
        None, ge=0, description="Maximum number of views."
    ),
    has_description: bool = Query(
        False, description="Filter to only include videos that have a description."
    ),
    es: AsyncElasticsearch = Depends(get_es_client),
) -> VideoSearchResponse:
    """
    Hybrid search endpoint:
    - Plain text search if `smart_search=False`
    - Hybrid text + vector search if `smart_search=True` and `query_vector` is provided
    """

    must_query = {
        "multi_match": {
            "query": q,
            "fields": ["name^3", "description^2"],
            "fuzziness": "AUTO",
        }
    }

    # Build filters dynamically
    filters: list[dict[str, dict]] = []

    if category:
        filters.append({"term": {"category": category}})

    if min_views is not None or max_views is not None:
        range_filter: dict[str, Any] = {"range": {"views": {}}}
        if min_views is not None:
            range_filter["range"]["views"]["gte"] = min_views
        if max_views is not None:
            range_filter["range"]["views"]["lte"] = max_views
        filters.append(range_filter)

    if has_description:
        filters.append({"exists": {"field": "description"}})

    # Combine query + filters
    text_query = {
        "bool": {
            "must": [must_query],
            "filter": filters,
        }
    }

    # ────────────────────────────────────────────────
    # Case 1: Text-only search
    # ────────────────────────────────────────────────
    if not smart_search or not query_vector:
        result = await es.search(index="videos", query=text_query, size=limit)
        return VideoSearchResponse(
            results=[VideoResult(**hit["_source"]) for hit in result["hits"]["hits"]]
        )

    # ────────────────────────────────────────────────
    # Case 2: Hybrid search (text + vector)
    # ────────────────────────────────────────────────
    result = await es.search(
        index="videos",
        knn={
            "field": "video_embedding",
            "query_vector": query_vector,
            "k": limit,
            "num_candidates": 100,
        },
        _source=["id", "name", "description", "views", "category"],
        query=text_query,
        rank={"rrf": {}},  # Reciprocal Rank Fusion — merges text and vector results
    )

    return VideoSearchResponse(
        results=[VideoResult(**hit["_source"]) for hit in result["hits"]["hits"]]
    )
