from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

from src.api.dependencies.services import get_comment_service
from src.schemas.comments import CommentCreate, CommentPage, CommentRead
from src.schemas.endpoint import ErrorResponse
from src.schemas.reaction import ReactionRequest, ReactionResponse
from src.services import get_current_user_id
from src.services.comments import CommentService

router_comments = APIRouter(
    prefix="/api/comments",
    tags=["comments"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@router_comments.get(
    "/{video_id}",
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


@router_comments.post(
    "/{comment_id}/reaction",
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


@router_comments.post(
    "/{video_id}",
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


@router_comments.delete(
    "/{comment_id}",
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
