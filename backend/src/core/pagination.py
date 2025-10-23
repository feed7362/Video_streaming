from typing import Optional, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")  # SQLAlchemy model type


async def paginate_query(
    session: AsyncSession,
    model: Type[T],
    page: int = 1,
    size: int = 20,
    filters: Optional[list] = None,
    order_by=None,
) -> tuple[list[T], int]:
    """
    Generic pagination for SQLAlchemy async queries.

    Returns: (items, total)
    """
    filters = filters or []

    # Total count
    total = await session.scalar(
        select(func.count()).select_from(model).where(*filters)
    )

    # Page data
    stmt = select(model).where(*filters).offset((page - 1) * size).limit(size)
    if order_by is not None:
        stmt = stmt.order_by(order_by)

    result = await session.execute(stmt)
    items = list(result.scalars().all())

    return items, total
