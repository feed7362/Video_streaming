import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from uuid import NAMESPACE_DNS, UUID, uuid5

import aiofiles
import httpx
from fastapi import UploadFile
from sqlalchemy.dialects.postgresql import insert
from starlette.datastructures import Headers

from src.infrastructure import get_rabbit_broker
from src.infrastructure.database import async_session_maker
from src.infrastructure.s3_client import get_s3_client
from src.models import (
    Category,
    Channel,
    PrivacyStatus,
    ReactionType,
    Role,
    User,
    UserStatus,
    VideoStatus,
)
from src.services.files import FileService

SEED_FILE = Path(__file__).parent / "initial_data.json"


def deterministic_uuid(scope: str, name: str) -> UUID:
    """Generate deterministic UUID5 using a scope prefix."""
    return uuid5(NAMESPACE_DNS, f"{scope}:{name.lower()}")


USER_ID = deterministic_uuid("user", "John Doe")


def parse_date(date_string: str) -> datetime:
    """Safely converts an ISO string into a Python datetime object."""
    return datetime.fromisoformat(date_string)


async def seed_videos_via_service(session, user_id: UUID) -> None:
    """Seeds videos by pushing them through the actual business logic pipeline."""
    video_path = "./assets/1280_placeholder.mp4"
    thumb_path = "./assets/thumbnail.png"

    if not os.path.exists(video_path) or not os.path.exists(thumb_path):
        logging.warning("Assets missing. Skipping FileService video seeding.")
        return

    logging.info("Initializing infrastructure clients for FileService...")

    s3_client = get_s3_client()
    broker = await get_rabbit_broker()

    file_service = FileService(session=session, s3_client=s3_client, broker=broker)

    logging.info("Pushing video through business logic pipeline...")

    with open(video_path, "rb") as v_file, open(thumb_path, "rb") as t_file:
        video_upload = UploadFile(
            filename="1280_placeholder.mp4",
            file=v_file,
            headers=Headers({"content-type": "video/mp4"}),
        )
        thumb_upload = UploadFile(
            filename="thumbnail.png",
            file=t_file,
            headers=Headers({"content-type": "image/png"}),
        )

        try:
            response = await file_service.upload_video(
                video=video_upload,
                thumbnail=thumb_upload,
                name="Building an HLS Streaming Server",
                description="This video was seeded via the backend business logic pipeline!",
                privacy="public",
                category="Education",
                user_id=user_id,
            )
            logging.info(f"Successfully queued video! Response: {response}")
        except Exception as e:
            logging.error(f"Failed to seed video via FileService: {e}")


async def _fetch_media_files() -> None:
    """Download assets from the specified URL."""
    files_to_download = [
        {
            "url": "https://placeholdervideo.dev/1280x720",
            "filename": "1280_placeholder.mp4",
        },
        {
            "url": "https://placeholdervideo.dev/1920x1080",
            "filename": "1920_placeholder.mp4",
        },
        {
            "url": "https://placehold.co/600x400/000000/FFFFFF.png",
            "filename": "thumbnail.png",
        },
    ]

    # ---- Configuration ----
    download_folder = "./assets"
    os.makedirs(download_folder, exist_ok=True)

    # ---- Download Loop ----
    async with httpx.AsyncClient() as client:
        for file in files_to_download:
            local_path = os.path.join(download_folder, file["filename"])
            print(f"Downloading {file['url']} -> {local_path}")
            resp = await client.get(file["url"])
            resp.raise_for_status()
            async with aiofiles.open(local_path, "wb") as f:
                await f.write(resp.content)
            print(f"Saved: {local_path}")

    print("All files downloaded successfully.")


async def seed_initial_data() -> None:
    """Seed initial system data into the database safely (idempotent)."""

    # ---- Download Assets ----
    await _fetch_media_files()

    # ---- Read JSON ----
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    async with async_session_maker() as session:
        # ---- Roles ----
        roles = [
            {
                "id": deterministic_uuid("user_role", i["name"]),
                "name": i["name"],
                "description": i["description"],
            }
            for i in data.get("roles", [])
        ]
        await session.execute(
            insert(Role).values(roles).on_conflict_do_nothing(index_elements=["id"])
        )

        # ---- Reaction Types ----
        reactions = [
            {
                "id": deterministic_uuid("reaction_type", i["name"]),
                "name": i["name"],
                "path": i["path"],
            }
            for i in data.get("reaction_types", [])
        ]
        await session.execute(
            insert(ReactionType)
            .values(reactions)
            .on_conflict_do_nothing(index_elements=["id"])
        )

        # ---- Categories ----
        categories = [
            {
                "id": deterministic_uuid("video_category", i["name"]),
                "name": i["name"],
            }
            for i in data.get("categories", [])
        ]
        await session.execute(
            insert(Category)
            .values(categories)
            .on_conflict_do_nothing(index_elements=["id"])
        )

        # ---- Privacy Statuses ----
        privacy_statuses = [
            {
                "id": deterministic_uuid("privacy_status", i["name"]),
                "name": i["name"],
            }
            for i in data.get("privacy_statuses", [])
        ]
        await session.execute(
            insert(PrivacyStatus)
            .values(privacy_statuses)
            .on_conflict_do_nothing(index_elements=["id"])
        )

        # ---- User Statuses ----
        user_statuses = [
            {
                "id": deterministic_uuid("user_status", i["value"]),
                "value": i["value"],
            }
            for i in data.get("user_statuses", [])
        ]
        await session.execute(
            insert(UserStatus)
            .values(user_statuses)
            .on_conflict_do_nothing(index_elements=["id"])
        )

        # ---- Video Statuses ----
        video_statuses = [
            {
                "id": deterministic_uuid("video_status", i["value"]),
                "value": i["value"],
            }
            for i in data.get("video_statuses", [])
        ]
        await session.execute(
            insert(VideoStatus)
            .values(video_statuses)
            .on_conflict_do_nothing(index_elements=["id"])
        )

        # ---- Users ----
        users = [
            {
                "id": USER_ID,
                "username": "John Doe",
                "email": "name@gmail.com",
                "hashed_password": "password",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
                "status_id": deterministic_uuid("user_status", "active"),
                "role_id": deterministic_uuid("user_role", "admin"),
                "created_at": parse_date("2023-01-01T00:00:00+00:00"),
            }
        ]

        await session.execute(
            insert(User)
            .values(users)
            .on_conflict_do_nothing(index_elements=["username"])
        )

        # ---- Channels ----
        channels = [
            {
                "id": deterministic_uuid("channels", i["name"]),
                "name": i["name"],
                "user_id": USER_ID,
                "subscribers_count": 0,
                "description": "test_channel_description",
                "views_count": 0,
                "avatar_path": i["avatar_path"].replace(
                    "NONE", str(deterministic_uuid("channels", i["name"]))
                ),
                "background_path": i["avatar_path"].replace(
                    "NONE", str(deterministic_uuid("channels", i["name"]))
                ),
                "created_at": parse_date("2023-01-01T00:00:00+00:00"),
            }
            for i in data.get("channels", [])
        ]

        await session.execute(
            insert(Channel)
            .values(channels)
            .on_conflict_do_nothing(index_elements=["id"])
        )

        await session.commit()
        logging.info("Initial data seeded successfully.")

        await seed_videos_via_service(session, USER_ID)
        logging.info("Videos seeded successfully.")


def main() -> None:
    asyncio.run(seed_initial_data())


if __name__ == "__main__":
    main()
