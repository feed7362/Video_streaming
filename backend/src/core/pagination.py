from typing import Any, Callable, List, Optional, Tuple, Type, TypeVar, cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")  # SQLAlchemy model type
U = TypeVar("U")


async def paginate_query(
    session: AsyncSession,
    model: Type[T],
    page: int = 1,
    size: int = 20,
    filters: Optional[List[Any]] = None,
    order_by: Any = None,
    preload: Optional[List[Any]] = None,
    mapper: Optional[Callable[[T], U]] = None,
) -> Tuple[List[U], int]:
    """
    Generic pagination for SQLAlchemy async queries.

    Returns: (items, total)
    """
    filters = filters or []
    preload = preload or []

    total = (
        await session.scalar(select(func.count()).select_from(model).where(*filters))
        or 0
    )

    stmt = select(model).where(*filters)
    for opt in preload:
        stmt = stmt.options(opt)
    if order_by is not None:
        stmt = stmt.order_by(order_by)

    stmt = stmt.offset((page - 1) * size).limit(size)
    result = await session.execute(stmt)
    raw_items = list(result.scalars().all())
    if mapper is not None:
        items: List[U] = [mapper(v) for v in raw_items]
    else:
        items = cast(List[U], raw_items)
    return items, total
