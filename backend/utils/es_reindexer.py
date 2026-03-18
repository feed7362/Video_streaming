import asyncio
import logging
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from src.infrastructure.database import async_session_maker
from src.infrastructure.elasticsearch import get_es_client
from src.models.video import Video


async def reindex_videos_from_db(batch_size: int = 500) -> None:
    """Reindex all videos from the database into Elasticsearch."""

    es = await get_es_client()

    logging.info("[ES] Starting video reindex")

    total_indexed = 0

    async with async_session_maker() as session:
        offset = 0

        while True:
            result = await session.execute(
                select(Video)
                .order_by(Video.created_at.desc())
                .options(
                    joinedload(Video.channel),
                    selectinload(Video.category),
                )
                .offset(offset)
                .limit(batch_size)
            )

            videos = result.scalars().all()

            if not videos:
                break

            operations: List[Dict[str, Any]] = []

            for v in videos:
                name = str(v.name).strip()
                description = str(v.description).strip()
                category = v.category.name.split() if v.category else []

                suggestion_inputs = [name]

                if description:
                    suggestion_inputs.append(description)

                doc = {
                    "id": str(v.id),
                    "name": name,
                    "description": description,
                    "channel_id": str(v.channel_id),
                    "category": category,
                    "views": v.views_count or 0,
                    "suggest_name": {
                        "input": suggestion_inputs,
                        "weight": v.views_count or 1,
                    },
                }

                operations.append({"index": {"_index": "videos", "_id": doc["id"]}})
                operations.append(doc)

            resp = await es.bulk(operations=operations)

            if resp.get("errors"):
                for item in resp["items"]:
                    if "error" in item["index"]:
                        err = item["index"]["error"]
                        logging.warning(
                            f"[ES] Index error: {err.get('type')} - {err.get('reason')}"
                        )

            total_indexed += len(videos)
            offset += batch_size

    logging.info(f"[ES] Reindexed {total_indexed} videos")


def main() -> None:
    asyncio.run(reindex_videos_from_db())


if __name__ == "__main__":
    main()
