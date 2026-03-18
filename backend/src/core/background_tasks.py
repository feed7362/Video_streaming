import logging

from elasticsearch import AsyncElasticsearch, NotFoundError


async def index_video_in_es(video: dict, es: AsyncElasticsearch) -> None:
    """Quick metadata index after upload (runs inside the FastAPI process)."""

    await es.index(
        index="videos",
        id=str(video["id"]),
        document={
            "name": video["name"],
            "description": video.get("description"),
            "user_id": str(video.get("user_id")) if video.get("user_id") else None,
            "channel_id": (
                str(video.get("channel_id")) if video.get("channel_id") else None
            ),
            "category": video.get("category"),
            "views": video.get("views", 0),
            "suggest_name": video["name"],
        },
    )


async def deindex_video_in_es(video_id: str, es: AsyncElasticsearch) -> None:
    """Safely delete it from Elasticsearch."""
    try:
        await es.delete(index="videos", id=str(video_id))
    except NotFoundError:
        logging.warning(
            f"Video {video_id} not found in Elasticsearch or already deleted."
        )


async def update_video_in_es(video: dict, es: AsyncElasticsearch) -> None:
    """Update metadata in ES."""
    try:
        await es.update(
            index="videos",
            id=str(video["id"]),
            document={
                "name": video["name"],
                "description": video.get("description"),
                "user_id": (
                    str(video.get("user_id")) if video.get("user_id") else None
                ),  # Use .get()
                "channel_id": (
                    str(video.get("channel_id")) if video.get("channel_id") else None
                ),
                "category": video.get("category"),
                "views": video.get("views", 0),
                "suggest_name": video["name"],
            },
        )
    except NotFoundError:
        logging.warning(
            f"Video {video.get('id')} not found in Elasticsearch for update."
        )
