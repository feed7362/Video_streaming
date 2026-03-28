from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.dependencies.metrics import video_search_metrics
from src.api.dependencies.services import get_search_service
from src.schemas.endpoint import ErrorResponse
from src.schemas.search import (
    VideoHintQuery,
    VideoHintsResponse,
    VideoResult,
    VideoSearchRequest,
    VideoSearchResponse,
)
from src.services.search import SearchService

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
    payload: Annotated[VideoHintQuery, Depends()],
    service: SearchService = Depends(get_search_service),
) -> VideoHintsResponse:
    """
    Returns autocomplete hints for the user's partial query.
    Uses Elasticsearch completion suggester.
    """
    hints = await service.get_video_hints(payload.query)
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
    dependencies=[Depends(video_search_metrics)],
)
async def video_search(
    payload: VideoSearchRequest,
    service: SearchService = Depends(get_search_service),
) -> VideoSearchResponse:
    """
    Hybrid search endpoint:
    - Plain text search if `smart_search=False`
    - Hybrid text + vector search if `smart_search=True` and `query_vector` is provided
    """

    result = await service.search_video(
        payload.query,
        payload.query_vector,
        payload.category,
        payload.min_views,
        payload.max_views,
        payload.limit,
        payload.smart_search,
        payload.has_description,
    )

    return VideoSearchResponse(results=[VideoResult(**hit) for hit in result["hits"]])
