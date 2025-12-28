import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from src.infrastructure.database import async_session_maker
from src.infrastructure.elasticsearch import get_es_client
from src.models.video import Video


async def reindex_videos_from_db(
    interval_minutes: int = 5,
    batch_size: int = 500,
) -> None:
    """Periodically reindex all videos from DB to Elasticsearch."""
    try:
        es = await get_es_client()
        while True:
            await asyncio.sleep(interval_minutes * 60)
            start = datetime.now()
            logging.info(
                f"[ES] Starting periodic reindex from DB at {start.isoformat()}"
            )

            try:
                async with async_session_maker() as session:
                    offset = 0
                    total_indexed = 0

                    while True:
                        result = await session.execute(
                            select(Video)
                            .order_by(Video.created_at.desc())
                            .options(
                                joinedload(Video.channel),  # preload channel
                                selectinload(Video.category),  # preload category
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
                            category = str(v.category.name).split()

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
                            operations.append(
                                {"index": {"_index": "videos", "_id": doc["id"]}}
                            )
                            operations.append(doc)

                        resp = await es.bulk(operations=operations)
                        total_indexed += len(operations) // 2

                        if resp.get("errors"):
                            for item in resp["items"]:
                                if "error" in item["index"]:
                                    err = item["index"]["error"]
                                    logging.warning(
                                        f"[ES] Index error: {err.get('type')} - {err.get('reason')}"
                                    )

                        offset += batch_size

                elapsed = (datetime.now() - start).total_seconds()
                logging.info(
                    f"[ES] Reindex {total_indexed} videos in {elapsed:.1f}s at {datetime.now()}"
                )
            except Exception as e:
                logging.error(f"[ES] Reindex run failed: {e}")

    except asyncio.CancelledError:
        logging.info("[ES] Reindex task cancelled cleanly.")
