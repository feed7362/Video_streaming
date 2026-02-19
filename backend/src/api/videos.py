from typing import List, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

from src.api.dependencies.services import get_comment_service, get_video_service
from src.schemas.comments import CommentCreate, CommentPage, CommentRead
from src.schemas.endpoint import ErrorResponse
from src.schemas.privacy import PrivacyLevel, PrivacyResponse
from src.schemas.reaction import ReactionRequest, ReactionResponse
from src.schemas.video import VideoPage, VideoPlayback, VideoPreviewPage
from src.services.auth import get_current_user_id
from src.services.comments import CommentService
from src.services.videos import VideoService

router_videos = APIRouter(
    prefix="/api/video",
    tags=["videos"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@router_videos.get(
    "/info/{video_id}",
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
    user_id: UUID = Depends(get_current_user_id),
    service: VideoService = Depends(get_video_service),
) -> VideoPlayback:
    return await service.get_playback(video_id=video_id, user_id=user_id)


@router_videos.get(
    "/get_comments/{video_id}",
    response_model=CommentPage,
    summary="List comments for a video",
    description="Returns a paginated list of comments belonging to the specified video.",
    response_description="Paginated comment list.",
    responses={
        200: {
            "model": CommentPage,
            "description": "Comments retrieved successfully.",
        },
        400: {
            "model": ErrorResponse,
            "description": "Invalid pagination parameters provided.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Video not found or has no comments.",
        },
        500: {
            "model": ErrorResponse,
            "description": "Unexpected error occurred while retrieving comments.",
        },
    },
)
async def get_comments(
    video_id: UUID = Path(
        ..., description="UUID of the video whose comments are requested."
    ),
    page: int = Query(1, ge=1, description="Page number for paginated results."),
    size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of comments to include per page (1-100).",
    ),
    service: CommentService = Depends(get_comment_service),
) -> CommentPage:
    comments, total = await service.get_by_video(video_id, page, size)
    return CommentPage(items=comments, page=page, size=size, total=total)


@router_videos.get(
    "/get_videos",
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
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    service: VideoService = Depends(get_video_service),
) -> VideoPreviewPage:
    videos, total = await service.list_videos(page=page, size=size)
    return VideoPreviewPage(items=videos, page=page, size=size, total=total)


@router_videos.get(
    "/get_videos/{category}",
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
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    category: Literal[
        "education",
        "entertainment",
        "music",
        "gaming",
        "technology",
        "science",
        "movies",
        "sports",
        "news",
        "travel",
        "lifestyle",
        "fashion",
        "health & fitness",
        "food & cooking",
        "comedy",
        "documentary",
        "art & design",
        "business & finance",
        "animals & nature",
        "automotive",
        "history",
        "podcasts",
        "shorts",
    ] = Path(description="Category of videos to filter by."),
    service: VideoService = Depends(get_video_service),
) -> VideoPreviewPage:
    videos, total = await service.list_videos(page=page, size=size, category=category)
    return VideoPreviewPage(items=videos, page=page, size=size, total=total)


@router_videos.get(
    "/get_categories",
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
) -> List[str]:
    return await service.list_categories()


@router_videos.post(
    "/reaction/video/{video_id}",
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


@router_videos.post(
    "/reaction/comment/{comment_id}",
    response_model=ReactionResponse,
    summary="Change comment reaction",
    description="Adds or removes a user's reaction (like, dislike, funny, etc.) to a specific comment.",
    response_description="Updated reaction count for the comment.",
    responses={
        200: {
            "model": CommentPage,
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
async def react_to_comment(
    comment_id: UUID,
    payload: ReactionRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: CommentService = Depends(get_comment_service),
) -> ReactionResponse:
    counts = await service.react(comment_id, user_id, payload.reaction_name)
    return ReactionResponse(
        target_id=comment_id,
        target_type="comment",
        reactions=counts,
    )


@router_videos.post(
    "/comment/{video_id}",
    response_model=CommentRead,
    summary="Add a comment to a video",
    description="Adds a new comment to the specified video.",
    responses={
        201: {"model": CommentRead, "description": "Comment created successfully."},
        404: {"model": ErrorResponse, "description": "Video not found."},
        400: {"model": ErrorResponse, "description": "Invalid data."},
        500: {"model": ErrorResponse, "description": "Internal server error."},
    },
    status_code=201,
)
async def add_comment(
    video_id: UUID,
    payload: CommentCreate,
    parent_id: UUID | None = Query(
        None, description="Optional ID of the parent comment to reply to."
    ),
    user_id: UUID = Depends(get_current_user_id),
    service: CommentService = Depends(get_comment_service),
) -> CommentRead:
    return await service.create(
        video_id=video_id, user_id=user_id, content=payload.content, parent_id=parent_id
    )


@router_videos.delete(
    "/comment/{comment_id}",
    summary="Delete a comment",
    description="Deletes a comment if the current user is its author or the owner of the video.",
    responses={
        204: {"description": "Comment deleted successfully."},
        403: {
            "model": ErrorResponse,
            "description": "Not authorized to delete this comment.",
        },
        404: {"model": ErrorResponse, "description": "Comment not found."},
        500: {"model": ErrorResponse, "description": "Internal server error."},
    },
    status_code=204,
)
async def delete_comment(
    comment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: CommentService = Depends(get_comment_service),
) -> None:
    """Delete a comment (only allowed by the comment author or video owner)."""

    await service.delete(comment_id=comment_id, user_id=user_id)


@router_videos.patch(
    "/privacy/{video_id}",
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
