from src.core.base_error import AppError


class InvalidReactionTypeError(AppError):
    code = "INVALID_REACTION_TYPE"
    status_code = 400

    def __init__(self, reaction_name: str):
        super().__init__(message=f"Unknown reaction type '{reaction_name}'")
