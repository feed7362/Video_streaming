from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

from src.api.dependencies.services import get_video_service
from src.schemas.endpoint import ErrorResponse, PaginationQuery
from src.schemas.privacy import PrivacyLevel, PrivacyResponse
from src.schemas.reaction import ReactionRequest, ReactionResponse
from src.schemas.video import VideoCategory, VideoPage, VideoPlayback, VideoPreviewPage
from src.services.auth import get_current_user_id, get_optional_user_id
from src.services.videos import VideoService

router_videos = APIRouter(
    prefix="/api/videos",
    tags=["videos"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@router_videos.get(
    "/",
    response_model=VideoPreviewPage,
    summary="List all videos",
    description="Returns a paginated list of videos with metadata such as title, duration, and status.",
    response_description="A paginated list of videos.",
    responses={
        200: {
            "model": VideoPreviewPage,
            "description": "List of videos successfully retrieved.",
        },
        400: {
            "model": ErrorResponse,
            "description": "Invalid query parameters (e.g., invalid page/size).",
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error.",
        },
    },
)
async def get_videos(
    payload: Annotated[PaginationQuery, Depends()],
    service: VideoService = Depends(get_video_service),
) -> VideoPreviewPage:
    videos, total = await service.list_videos(page=payload.page, size=payload.size)
    return VideoPreviewPage(
        items=videos, page=payload.page, size=payload.size, total=total
    )


@router_videos.get(
    "/categories",
    response_model=List[str],
    summary="List all videos of categories",
    description="Returns a list of distinct video category Name.",
    response_description="List of unique category Name.",
    responses={
        200: {
            "model": List[str],
            "description": "List of categories successfully retrieved.",
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error.",
        },
    },
)
async def get_categories(
    service: VideoService = Depends(get_video_service),
    plain: bool = Query(True, description="Return plain list of category names"),
) -> List[str]:
    return await service.list_categories(plain=plain)


@router_videos.get(
    "/{video_id}",
    response_model=VideoPlayback,
    summary="Get video playback information",
    description="Retrieves metadata and playback details for a specific video.",
    response_description="Metadata describing the requested video.",
    responses={
        200: {
            "model": VideoPlayback,
            "description": "Video metadata retrieved successfully.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Video metadata could not be found.",
        },
        500: {
            "model": ErrorResponse,
            "description": "Unexpected error occurred while retrieving metadata.",
        },
    },
)
async def get_video_info(
    video_id: UUID = Path(
        ..., description="UUID of the video to retrieve playback info for."
    ),
    user_id: UUID | None = Depends(get_optional_user_id),
    service: VideoService = Depends(get_video_service),
) -> VideoPlayback:
    return await service.get_playback(video_id=video_id, user_id=user_id)


@router_videos.get(
    "/categories/{category}",
    response_model=VideoPreviewPage,
    summary="List all videos by category",
    description="Returns a paginated list of videos by category.",
    response_description="A paginated list of videos by category.",
    responses={
        200: {
            "model": VideoPreviewPage,
            "description": "List of videos successfully retrieved.",
        },
        400: {
            "model": ErrorResponse,
            "description": "Invalid query parameters (e.g., invalid page/size).",
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error.",
        },
    },
)
async def get_videos_category(
    query: Annotated[PaginationQuery, Depends()],
    category: VideoCategory = Path(description="Category of videos to filter by."),
    service: VideoService = Depends(get_video_service),
) -> VideoPreviewPage:
    videos, total = await service.list_videos(
        page=query.page, size=query.size, category=category
    )
    return VideoPreviewPage(items=videos, page=query.page, size=query.size, total=total)


@router_videos.post(
    "/{video_id}/reactions",
    response_model=ReactionResponse,
    summary="Change video reaction",
    description="Adds or removes a user's reaction (like, love, funny, etc.) to a specific video.",
    response_description="Updated like and dislike counts for the video.",
    responses={
        200: {
            "model": VideoPage,
            "description": "Reactions successfully retrieved.",
        },
        400: {
            "model": ErrorResponse,
            "description": "Invalid parameters (e.g., invalid like/dislike count).",
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error.",
        },
    },
)
async def react_to_video(
    video_id: UUID,
    payload: ReactionRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: VideoService = Depends(get_video_service),
) -> ReactionResponse:
    counts = await service.react(video_id, user_id, payload.reaction_name)
    return ReactionResponse(
        target_id=video_id,
        target_type="video",
        reactions=counts,
    )


@router_videos.patch(
    "/{video_id}/privacy",
    summary="Update video privacy",
    response_model=PrivacyResponse,
    description="Update the privacy visibility of the specified video (public/private).",
    response_description="Updated PrivacyLevel setting.",
    responses={
        200: {
            "model": PrivacyResponse,
            "description": "PrivacyLevel successfully updated.",
        },
        403: {
            "model": ErrorResponse,
            "description": "Not allowed to update this resource.",
        },
        404: {"model": ErrorResponse, "description": "Video not found."},
        500: {"model": ErrorResponse, "description": "Internal server error."},
    },
)
async def update_privacy(
    video_id: UUID,
    updated_privacy: PrivacyLevel = Query(
        default="public",
        description="Privacy setting: `public` or `private`",
        examples=["public", "private"],
    ),
    user_id: UUID = Depends(get_current_user_id),
    service: VideoService = Depends(get_video_service),
) -> PrivacyResponse:
    old_privacy, new_privacy = await service.update_privacy(
        video_id=video_id, user_id=user_id, privacy_name=updated_privacy
    )
    return PrivacyResponse(
        video_id=video_id,
        old_privacy=old_privacy,
        updated_privacy=new_privacy,
    )
