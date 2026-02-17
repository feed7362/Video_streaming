from uuid import NAMESPACE_DNS, UUID, uuid4, uuid5

from fastapi import Depends
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.database import get_async_session
from ..models import Channel, User


async def get_current_user_id(
    # current_user = Depends(get_current_user)
    session: AsyncSession = Depends(get_async_session),
) -> UUID:
    user_id = UUID("04a41021-ad20-4e8b-b11e-7781ec042903")
    user = await session.get(User, user_id)

    if user is None:
        await session.execute(
            insert(User).values(
                id=user_id,
                username="John Doe",
                email="name@gmail.com",
                hash_password="password",
                status_id=uuid5(NAMESPACE_DNS, "user_status:active"),
                role_id=uuid5(NAMESPACE_DNS, "user_role:user"),
            )
        )
        await session.execute(
            insert(Channel).values(
                id=uuid4(), channel_name="John Doe`s channel", user_id=user_id
            )
        )
        await session.flush()
    return user_id
