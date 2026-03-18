from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.requests import Request

from src.infrastructure import get_redis
from src.infrastructure.redis.rate_limiter import RateLimiter


async def get_rate_limiter(redis=Depends(get_redis)) -> RateLimiter:
    return RateLimiter(redis)


def limit_requests(endpoint: str, max_requests: int, window_seconds: int):
    """
    Factory function to create a custom dependency for each endpoint
    Example usage:
    @router_files.post(
        "/upload",
        response_model=UploadResponse,
        dependencies=[Depends(limit_requests("upload_files", max_requests=5, window_seconds=60))]
    )
    """

    async def dependency(
        request: Request,
        limiter: Annotated[RateLimiter, Depends(get_rate_limiter)],
    ):
        # Identify by IP (or user ID if available)
        identifier = request.client.host

        is_limited = await limiter.is_limited(
            ip_address=identifier,
            endpoint=endpoint,
            max_requests=max_requests,
            window_seconds=window_seconds,
        )

        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please cool down.",
            )

    return dependency
