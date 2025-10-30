import logging
import uuid
from datetime import datetime
from ..schemas.enum import Privacy

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from ..core.auth import get_current_user_id
from ..core.pagination import paginate_query
from ..core.video import (
    get_video_by_id,
    get_video_reaction,
    get_video_views,
    toggle_reaction,
)
from ..infrastructure.database import get_async_session
from ..models import Video, VideoReaction
from ..models.comments import Comment
from ..schemas.comments import CommentPage
from ..schemas.endpoint import APIError, ErrorResponse
from ..schemas.video import VideoPage, VideoPlayback
from ..schemas.video_reaction import ReactionRequest, ReactionResponse

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
    video_id: str = Path(
        ..., description="UUID of the video to retrieve playback info for."
    ),
) -> VideoPlayback:
    channel_name = "Channel Name"
    s3_video = f"{video_id}/master.m3u8"
    s3_thumbnail = f"{video_id}/thumbnail.jpg"
    s3_channel_avatar = f"{channel_name}/avatar.jpg"
    try:
        logging.info(f"Streaming playlist master: {video_id}")
        return VideoPlayback(
            id=uuid.UUID(video_id),
            name="test.mp4",
            description="Test Description",
            created_at=datetime.now(),
            master_hls_url=f"/minio/videos/{s3_video}",
            privacy=Privacy.PUBLIC,
            resolutions=["360p", "720p"],
            channel_name="Channel Name",
            likes_count=123,
            views_count=111,
            dislikes_count=22,
            thumbnail_url=f"/minio/thumbnail/{s3_thumbnail}",
            avatar_url=f"/minio/avatar/{s3_channel_avatar}",
        )
    except Exception as e:
        logging.error(f"Error streaming file: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(message=str(e)).model_dump(),
        )


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
            "model": APIError,
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
    video_id: uuid.UUID = Path(
        ..., description="UUID of the video whose comments are requested."
    ),
    page: int = Query(1, ge=1, description="Page number for paginated results."),
    size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of comments to include per page (1-100).",
    ),
    session: AsyncSession = Depends(get_async_session),
) -> CommentPage:
    filters = [Comment.video_id == video_id]

    comments, total = await paginate_query(
        session=session,
        model=Comment,
        page=page,
        size=size,
        filters=filters,
        order_by=Comment.created_at.desc(),
    )

    return CommentPage(items=comments, page=page, size=size, total=total)


@router_videos.get(
    "/get_videos",
    response_model=VideoPage,
    summary="List all videos",
    description="Returns a paginated list of videos with metadata such as title, duration, and status.",
    response_description="A paginated list of videos.",
    responses={
        200: {
            "model": VideoPage,
            "description": "List of videos successfully retrieved.",
        },
        400: {
            "model": APIError,
            "description": "Invalid query parameters (e.g., invalid page/size).",
        },
        500: {
            "model": APIError,
            "description": "Internal server error.",
        },
    },
)
async def get_videos(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    session: AsyncSession = Depends(get_async_session),
) -> VideoPage:
    videos, total = await paginate_query(
        session=session,
        model=Video,
        page=page,
        size=size,
        order_by=Video.created_at.desc(),
    )
    return VideoPage(items=videos, page=page, size=size, total=total)


@router_videos.post(
    "/reaction/{video_id}",
    response_model=ReactionResponse,
    summary="Change video reaction",
    description="Like or dislike a video.",
    response_description="Updated like and dislike counts for the video.",
    responses={
        200: {
            "model": VideoPage,
            "description": "Reactions successfully retrieved.",
        },
        400: {
            "model": APIError,
            "description": "Invalid parameters (e.g., invalid like/dislike count).",
        },
        500: {
            "model": APIError,
            "description": "Internal server error.",
        },
    },
)
async def react_to_video(
    like_data: ReactionRequest,
    video_id: uuid.UUID = Path(
        ..., description="UUID of the video whose video to like/dislike."
    ),
    session: AsyncSession = Depends(get_async_session),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    Like or dislike a video.
    Send `{"is_like": true}` for like, or `{"is_like": false}` for dislike.
    """
    likes, dislikes = await toggle_reaction(
        session=session,
        like_model=VideoReaction,
        target_id_field=VideoReaction.video_id,
        target_id=video_id,
        user_id=user_id,
        is_like=like_data.is_like,
    )

    return ReactionResponse(video_id=video_id, likes=likes, dislikes=dislikes)
