from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from ..schemas.endpoint import ErrorResponse
from ..schemas.search import VideoHintsResponse, VideoResult, VideoSearchResponse
from ..services.search import SearchService
from .dependencies.metrics import video_search_metrics
from .dependencies.services import get_search_service

router_search = APIRouter(
    prefix="/api/search",
    tags=["search"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


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
    service: SearchService = Depends(get_search_service),
) -> VideoHintsResponse:
    """
    Returns autocomplete hints for the user's partial query.
    Uses Elasticsearch completion suggester.
    """
    hints = await service.get_video_hints(q)
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
    query: str = Query(
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
    service: SearchService = Depends(get_search_service),
    _metrics=Depends(video_search_metrics),
) -> VideoSearchResponse:
    """
    Hybrid search endpoint:
    - Plain text search if `smart_search=False`
    - Hybrid text + vector search if `smart_search=True` and `query_vector` is provided
    """

    result = await service.search_video(
        query,
        query_vector,
        category,
        min_views,
        max_views,
        limit,
        smart_search,
        has_description,
    )

    return VideoSearchResponse(results=[VideoResult(**hit) for hit in result["hits"]])
