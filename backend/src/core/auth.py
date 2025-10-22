import uuid

# from fastapi import Depends
# from ..core.security import get_current_user


def get_current_user_id(
    # current_user = Depends(get_current_user)
):
    return uuid.uuid4()  # current_user.id
