from src.core.base_error import AppError


class CommentNotFoundError(AppError):
    code = "COMMENT_NOT_FOUND"
    status_code = 404
    message = "Comment not found"


class ParentCommentNotFoundError(AppError):
    code = "PARENT_COMMENT_NOT_FOUND"
    status_code = 404
    message = "Parent comment not found"


class CommentDeleteForbiddenError(AppError):
    code = "COMMENT_DELETE_FORBIDDEN"
    status_code = 403
    message = "Not allowed to delete this comment"


class ParentCommentVideoMismatchError(AppError):
    code = "PARENT_COMMENT_VIDEO_MISMATCH"
    status_code = 400
    message = "Parent comment belongs to a different video"
