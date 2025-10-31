from typing import Callable, Optional, Type, TypeVar

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
    preload: Optional[list] = None,
    mapper: Optional[Callable] = None,
) -> tuple[list[T], int]:
    """
    Generic pagination for SQLAlchemy async queries.

    Returns: (items, total)
    """
    filters = filters or []
    preload = preload or []

    total = await session.scalar(
        select(func.count()).select_from(model).where(*filters)
    )

    stmt = select(model).where(*filters)
    for opt in preload:
        stmt = stmt.options(opt)
    if order_by is not None:
        stmt = stmt.order_by(order_by)

    stmt = stmt.offset((page - 1) * size).limit(size)
    result = await session.execute(stmt)
    raw_items = list(result.scalars().all())
    items = [mapper(v) for v in raw_items] if mapper else raw_items

    return items, total
