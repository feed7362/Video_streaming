from src.core.base_error import AppError
from src.i18n import _


class InvalidReactionTypeError(AppError):
    code = "INVALID_REACTION_TYPE"
    status_code = 400

    def __init__(self, reaction_name: str):
        super().__init__(
            _("Unknown reaction type '%(reaction_name)s'")
            % {"reaction_name": reaction_name}
        )
