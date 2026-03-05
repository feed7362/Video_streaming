from uuid import NAMESPACE_DNS, UUID, uuid4, uuid5

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database import get_async_session
from src.models import Channel, User


async def get_current_user_id(
    # current_user = Depends(get_current_user)
    session: AsyncSession = Depends(get_async_session),
) -> UUID:
    target_username = "John Doe"

    user_stmt = (
        insert(User)
        .values(
            id=UUID("04a41021-ad20-4e8b-b11e-7781ec042903"),
            username=target_username,
            email="name@gmail.com",
            hash_password="password",
            status_id=uuid5(NAMESPACE_DNS, "user_status:active"),
            role_id=uuid5(NAMESPACE_DNS, "user_role:user"),
        )
        .on_conflict_do_nothing(index_elements=["username"])
    )

    await session.execute(user_stmt)

    result = await session.execute(
        select(User.id).where(User.username == target_username)
    )
    real_user_id = result.scalar_one()

    channel_stmt = (
        insert(Channel)
        .values(id=uuid4(), name=f"{target_username}'s channel", user_id=real_user_id)
        .on_conflict_do_nothing(index_elements=["user_id"])
    )

    await session.execute(channel_stmt)

    await session.commit()

    return real_user_id
