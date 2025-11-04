import logging
from typing import List, Literal
from uuid import NAMESPACE_DNS, UUID, uuid5

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.responses import JSONResponse

from ..core.auth import get_current_user_id
from ..core.pagination import paginate_query
from ..core.video import (
    get_video_by_id,
    record_video_view,
    toggle_reaction,
)
from ..infrastructure.database import get_async_session
from ..models import (
    Category,
    Channel,
    CommentReaction,
    PrivacyStatus,
    Video,
    VideoReaction,
)
from ..models.comments import Comment
from ..schemas.comments import CommentPage, to_comment_read
from ..schemas.endpoint import APIError, ErrorResponse
from ..schemas.privacy import PrivacyLevel, PrivacyResponse
from ..schemas.reaction import ReactionRequest, ReactionResponse
from ..schemas.video import VideoPage, VideoPlayback, VideoPreviewPage, to_video_preview

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
    session: AsyncSession = Depends(get_async_session),
    user_id: UUID = Depends(get_current_user_id),
) -> VideoPlayback:
    try:
        video, resolutions = await get_video_by_id(video_id, session)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        await record_video_view(session, video_id=video.id, user_id=user_id)
        logging.info(f"Streaming playlist master: {video_id}")
        return VideoPlayback(
            id=video.id,
            name=video.name,
            description=video.description,
            created_at=video.created_at,
            master_hls_url=video.video_path,
            privacy=video.privacy.name,
            resolutions=resolutions,
            channel_name=video.channel.channel_name,
            likes_count=video.likes_count,
            dislikes_count=video.dislikes_count,
            views_count=video.views_count + 1,
            thumbnail_url=video.thumbnail_path,
            avatar_url=video.channel.avatar_path,
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
        mapper=to_comment_read,
    )

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
) -> VideoPreviewPage:
    filters = [
        Video.privacy_id == uuid5(NAMESPACE_DNS, "privacy_status:public"),
        Video.status_id == uuid5(NAMESPACE_DNS, "video_status:ready"),
    ]
    preload = [
        selectinload(Video.channel),
        selectinload(Video.privacy),
        selectinload(Video.resolutions),
    ]
    videos, total = await paginate_query(
        session=session,
        model=Video,
        page=page,
        size=size,
        filters=filters,
        preload=preload,
        order_by=Video.created_at.desc(),
        mapper=to_video_preview,
    )
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
            "model": APIError,
            "description": "Invalid query parameters (e.g., invalid page/size).",
        },
        500: {
            "model": APIError,
            "description": "Internal server error.",
        },
    },
)
async def get_videos_category(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    session: AsyncSession = Depends(get_async_session),
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
) -> VideoPreviewPage:
    filters = [
        Video.privacy_id == uuid5(NAMESPACE_DNS, "privacy_status:public"),
        Video.status_id == uuid5(NAMESPACE_DNS, "video_status:ready"),
        Video.category_id == uuid5(NAMESPACE_DNS, f"video_category:{category}"),
    ]
    preload = [
        selectinload(Video.channel),
        selectinload(Video.privacy),
        selectinload(Video.resolutions),
    ]
    videos, total = await paginate_query(
        session=session,
        model=Video,
        page=page,
        size=size,
        filters=filters,
        preload=preload,
        order_by=Video.created_at.desc(),
        mapper=to_video_preview,
    )
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
            "model": APIError,
            "description": "Internal server error.",
        },
    },
)
async def get_categories(
    session: AsyncSession = Depends(get_async_session),
) -> list[str]:
    result = await session.execute(
        select(Category.name)
        .join(Video, Category.id == Video.category_id)
        .distinct()
        .order_by(Category.name)
    )
    categories = result.scalars().all()

    return [str(c) for c in categories]


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
    video_id: UUID,
    payload: ReactionRequest,  # {"reaction_name": "like"}
    session: AsyncSession = Depends(get_async_session),
    user_id: UUID = Depends(get_current_user_id),
) -> ReactionResponse:
    counts = await toggle_reaction(
        session=session,
        user_id=user_id,
        target_model=VideoReaction,
        target_field=VideoReaction.video_id,
        target_id=video_id,
        reaction_name=payload.reaction_name,
    )
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
            "model": APIError,
            "description": "Invalid parameters (e.g., invalid like/dislike count).",
        },
        500: {
            "model": APIError,
            "description": "Internal server error.",
        },
    },
)
async def react_to_comment(
    comment_id: UUID,
    payload: ReactionRequest,
    session: AsyncSession = Depends(get_async_session),
    user_id: UUID = Depends(get_current_user_id),
) -> ReactionResponse:
    counts = await toggle_reaction(
        session=session,
        user_id=user_id,
        target_model=CommentReaction,
        target_field=CommentReaction.comment_id,
        target_id=comment_id,
        reaction_name=payload.reaction_name,
    )
    return ReactionResponse(
        target_id=comment_id,
        target_type="comment",
        reactions=counts,
    )


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
        403: {"model": APIError, "description": "Not allowed to update this resource."},
        404: {"model": APIError, "description": "Video not found."},
        500: {"model": APIError, "description": "Internal server error."},
    },
)
async def update_privacy(
    video_id: UUID,
    updated_privacy: PrivacyLevel = Query(
        default="public",
        description="Privacy setting: `public` or `private`",
        examples=["public", "private"],
    ),
    session: AsyncSession = Depends(get_async_session),
    user_id: UUID = Depends(get_current_user_id),
) -> PrivacyResponse:
    privacy_row = await session.scalar(
        select(PrivacyStatus).where(PrivacyStatus.name == updated_privacy)
    )
    if not privacy_row:
        raise HTTPException(400, f"Invalid privacy level '{updated_privacy}'")

    # Join to ensure this video belongs to the user's channel
    video = await session.scalar(
        select(Video)
        .options(selectinload(Video.privacy))
        .join(Channel)
        .where(Video.id == video_id, Channel.user_id == user_id)
    )
    if not video:
        raise HTTPException(403, "You do not own this video or it does not exist")

    old_privacy = video.privacy.name if video.privacy else "unknown"

    # Update the video privacy_id
    try:
        await session.execute(
            update(Video).where(Video.id == video_id).values(privacy_id=privacy_row.id)
        )
        await session.commit()
        await session.refresh(video)
    except Exception as e:
        await session.rollback()
        logging.error(f"Failed to update privacy: {e}")
        raise HTTPException(500, "Database error during privacy update")

    return PrivacyResponse(
        video_id=video_id,
        old_privacy=old_privacy,
        updated_privacy=updated_privacy,
    )
